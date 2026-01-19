import { ElMessage } from 'element-plus'

/**
 * WebRTC语音通话管理类
 */
export class VoiceCallManager {
  constructor() {
    this.localStream = null
    this.remoteStream = null
    this.peerConnection = null
    this.isCallActive = false
    this.isCaller = false
    this.callId = null
    this.socket = null
    this.iceServers = [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
  }

  /**
   * 初始化WebRTC连接
   */
  async initialize(socket, callId, isCaller = false) {
    this.socket = socket
    this.callId = callId
    this.isCaller = isCaller

    try {
      // 获取本地音频流
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        },
        video: false
      })

      // 创建RTCPeerConnection
      this.peerConnection = new RTCPeerConnection({
        iceServers: this.iceServers
      })

      // 添加本地音频轨道
      this.localStream.getTracks().forEach(track => {
        this.peerConnection.addTrack(track, this.localStream)
      })

      // 监听远程流
      this.peerConnection.ontrack = (event) => {
        this.remoteStream = event.streams[0]
        this.onRemoteStreamAdded(this.remoteStream)
      }

      // ICE候选处理
      this.peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.socket.emit('ice-candidate', {
            callId: this.callId,
            candidate: event.candidate
          })
        }
      }

      // 连接状态监听
      this.peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', this.peerConnection.connectionState)
        if (this.peerConnection.connectionState === 'connected') {
          this.isCallActive = true
          this.onCallConnected()
        } else if (this.peerConnection.connectionState === 'disconnected' || 
                   this.peerConnection.connectionState === 'failed') {
          this.onCallDisconnected()
        }
      }

      return true
    } catch (error) {
      console.error('初始化WebRTC失败:', error)
      ElMessage.error('无法访问麦克风，请检查权限设置')
      return false
    }
  }

  /**
   * 发起通话（创建offer）
   */
  async createOffer() {
    try {
      const offer = await this.peerConnection.createOffer()
      await this.peerConnection.setLocalDescription(offer)
      
      this.socket.emit('offer', {
        callId: this.callId,
        offer: offer
      })

      return true
    } catch (error) {
      console.error('创建offer失败:', error)
      ElMessage.error('发起通话失败')
      return false
    }
  }

  /**
   * 处理收到的offer
   */
  async handleOffer(offer) {
    try {
      await this.peerConnection.setRemoteDescription(offer)
      const answer = await this.peerConnection.createAnswer()
      await this.peerConnection.setLocalDescription(answer)
      
      this.socket.emit('answer', {
        callId: this.callId,
        answer: answer
      })

      return true
    } catch (error) {
      console.error('处理offer失败:', error)
      ElMessage.error('接听通话失败')
      return false
    }
  }

  /**
   * 处理收到的answer
   */
  async handleAnswer(answer) {
    try {
      await this.peerConnection.setRemoteDescription(answer)
      return true
    } catch (error) {
      console.error('处理answer失败:', error)
      ElMessage.error('通话连接失败')
      return false
    }
  }

  /**
   * 处理ICE候选
   */
  async handleIceCandidate(candidate) {
    try {
      await this.peerConnection.addIceCandidate(candidate)
      return true
    } catch (error) {
      console.error('处理ICE候选失败:', error)
      return false
    }
  }

  /**
   * 结束通话
   */
  async endCall() {
    if (this.peerConnection) {
      this.peerConnection.close()
      this.peerConnection = null
    }

    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop())
      this.localStream = null
    }

    this.isCallActive = false
    this.isCaller = false
    this.callId = null

    this.socket.emit('end-call', { callId: this.callId })
    this.onCallEnded()
  }

  /**
   * 静音/取消静音
   */
  toggleMute() {
    if (this.localStream) {
      const audioTracks = this.localStream.getAudioTracks()
      audioTracks.forEach(track => {
        track.enabled = !track.enabled
      })
      return !audioTracks[0].enabled
    }
    return false
  }

  /**
   * 获取本地音频流
   */
  getLocalStream() {
    return this.localStream
  }

  /**
   * 获取远程音频流
   */
  getRemoteStream() {
    return this.remoteStream
  }

  /**
   * 回调函数 - 需要在外部设置
   */
  onRemoteStreamAdded = (stream) => {}
  onCallConnected = () => {}
  onCallDisconnected = () => {}
  onCallEnded = () => {}
}

/**
 * 检查浏览器WebRTC支持
 */
export function checkWebRTCSupport() {
  return !!(navigator.mediaDevices && 
            navigator.mediaDevices.getUserMedia && 
            RTCPeerConnection)
}

/**
 * 获取音频设备列表
 */
export async function getAudioDevices() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    return devices.filter(device => device.kind === 'audioinput')
  } catch (error) {
    console.error('获取音频设备失败:', error)
    return []
  }
}