<template>
  <div class="role-selector">
    <el-popover
      v-model:visible="popoverVisible"
      placement="bottom-start"
      :width="400"
      trigger="click"
    >
      <template #reference>
        <el-button class="role-trigger-btn" :class="{ 'active': selectedRole }">
          <el-icon><User /></el-icon>
          <span>{{ selectedRole ? selectedRole.name : '角色扮演' }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
      </template>

      <div class="role-popover-content">
        <div class="role-header">
          <h4>选择角色</h4>
          <el-radio-group v-model="roleMode" size="small">
            <el-radio-button label="preset">预设角色</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
        </div>

        <div v-if="roleMode === 'preset'" class="role-grid">
          <div
            v-for="role in rolePresets"
            :key="role.id"
            class="role-card"
            :class="{ 'selected': selectedRole?.id === role.id }"
            @click="selectRole(role)"
          >
            <div class="role-icon">{{ getRoleIcon(role.name) }}</div>
            <div class="role-info">
              <div class="role-name">{{ role.name }}</div>
              <div class="role-desc">{{ role.description }}</div>
            </div>
          </div>
        </div>

        <div v-else class="custom-role-form">
          <el-form label-position="top">
            <el-form-item label="角色名称">
              <el-input v-model="customRoleName" placeholder="例如：严厉的数学老师" />
            </el-form-item>
            <el-form-item label="角色设定">
              <el-input
                v-model="customRolePrompt"
                type="textarea"
                :rows="4"
                placeholder="描述这个角色的性格、专业领域、说话风格等。例如：你是一位严厉的数学老师，擅长用生动的例子解释复杂的数学概念，对学生要求严格但充满耐心。"
              />
            </el-form-item>
            <el-button type="primary" @click="applyCustomRole" :disabled="!customRoleName || !customRolePrompt">
              应用角色
            </el-button>
          </el-form>
        </div>

        <div v-if="selectedRole" class="role-footer">
          <el-button size="small" type="danger" @click="clearRole">
            <el-icon><Close /></el-icon>
            清除角色
          </el-button>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, ArrowDown, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import service from '@/utils/request'

const emit = defineEmits(['role-change'])

const popoverVisible = ref(false)
const roleMode = ref('preset')
const rolePresets = ref([])
const selectedRole = ref(null)
const customRoleName = ref('')
const customRolePrompt = ref('')

const roleIcons = {
  '老师': '👨‍🏫',
  '医生': '👨‍⚕️',
  '朋友': '👫',
  '心理咨询师': '🧠',
  '厨师': '👨‍🍳',
  '程序员': '💻',
  '翻译官': '🌐',
  '作家': '✍️',
  '健身教练': '💪',
  '历史学家': '📚'
}

const getRoleIcon = (roleName) => {
  return roleIcons[roleName] || '🎭'
}

const loadRolePresets = async () => {
  try {
    const response = await service.get('/role-presets/')
    if (response.data && response.data.roles) {
      rolePresets.value = response.data.roles
    }
  } catch (error) {
    console.error('加载角色预设失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

const selectRole = (role) => {
  selectedRole.value = role
  emit('role-change', {
    role_id: role.id,
    custom_role_prompt: null,
    role_name: role.name
  })
  popoverVisible.value = false
  ElMessage.success(`已选择角色：${role.name}`)
}

const applyCustomRole = () => {
  if (!customRoleName.value || !customRolePrompt.value) {
    ElMessage.warning('请填写角色名称和角色设定')
    return
  }

  selectedRole.value = {
    id: 'custom',
    name: customRoleName.value,
    description: customRolePrompt.value
  }

  emit('role-change', {
    role_id: 'custom',
    custom_role_prompt: customRolePrompt.value,
    role_name: customRoleName.value
  })

  popoverVisible.value = false
  ElMessage.success(`已应用自定义角色：${customRoleName.value}`)
}

const clearRole = () => {
  selectedRole.value = null
  customRoleName.value = ''
  customRolePrompt.value = ''
  emit('role-change', null)
  ElMessage.info('已清除角色')
}

onMounted(() => {
  loadRolePresets()
})

defineExpose({
  selectedRole
})
</script>

<style scoped>
.role-selector {
  display: inline-block;
}

.role-trigger-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.role-trigger-btn.active {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.role-popover-content {
  padding: 0;
}

.role-header {
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.role-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.role-card:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.role-card.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.role-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.role-info {
  flex: 1;
  min-width: 0;
}

.role-name {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 4px;
}

.role-desc {
  font-size: 11px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-role-form {
  padding: 16px;
}

.role-footer {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}
</style>
