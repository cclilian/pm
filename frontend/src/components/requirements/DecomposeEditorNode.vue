<script setup lang="ts">
import DecomposeEditorNode from './DecomposeEditorNode.vue'

export interface DecomposeEditorNodeData {
  key: string
  title: string
  subtasks: DecomposeEditorNodeData[]
}

const props = withDefaults(
  defineProps<{
    node: DecomposeEditorNodeData
    depth: number
    canRemove: boolean
    titlePlaceholder?: string
    subButtonLabel?: string
  }>(),
  {
    titlePlaceholder: '任务标题',
    subButtonLabel: '子任务',
  },
)

const emit = defineEmits<{
  remove: []
  addSub: [node: DecomposeEditorNodeData]
}>()

function handleAddSub() {
  emit('addSub', props.node)
}
</script>

<template>
  <div class="editor-node" :style="{ marginLeft: `${depth * 20}px` }">
    <div class="editor-row">
      <el-input
        v-model="node.title"
        :placeholder="titlePlaceholder"
        maxlength="200"
        class="title-input"
      />
      <el-button type="primary" link @click="handleAddSub">{{ subButtonLabel }}</el-button>
      <el-button v-if="canRemove" type="danger" link @click="emit('remove')">删除</el-button>
    </div>

    <DecomposeEditorNode
      v-for="child in node.subtasks"
      :key="child.key"
      :node="child"
      :depth="depth + 1"
      :can-remove="true"
      :title-placeholder="titlePlaceholder"
      :sub-button-label="subButtonLabel"
      @remove="node.subtasks = node.subtasks.filter((item) => item.key !== child.key)"
      @add-sub="(parent) => emit('addSub', parent)"
    />
  </div>
</template>

<style scoped>
.editor-node {
  margin-bottom: 8px;
}

.editor-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-input {
  flex: 1;
}
</style>
