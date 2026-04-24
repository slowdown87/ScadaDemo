<template>
  <div class="test-container">
    <h1>测试页面</h1>
    <p>如果看到这个，说明Vue正常渲染</p>
    <button @click="testClick">点击测试</button>
    <p>当前时间: {{ time }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const time = ref('')

onMounted(() => {
  time.value = new Date().toLocaleTimeString()
  setInterval(() => {
    time.value = new Date().toLocaleTimeString()
  }, 1000)
})

function testClick() {
  alert('按钮点击正常!')
}
</script>

<style scoped>
.test-container {
  padding: 50px;
  text-align: center;
  background: #fff;
  color: #000;
}
</style>
