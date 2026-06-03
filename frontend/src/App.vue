<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <el-container class="layout">
    <el-header height="56px">
      <div class="brand">PM</div>
    </el-header>
    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}

.el-header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  background: #fff;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}
</style>
