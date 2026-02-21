<template>
  <div class="app">
    <header class="app-header">
      <h1>文言文记忆工具</h1>
      <nav class="app-nav">
        <RouterLink to="/">练习</RouterLink>
        <RouterLink to="/review">复习</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
    <footer class="app-footer">
      <p>基于错误驱动 + 艾宾浩斯遗忘曲线</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.app-nav {
  display: flex;
  gap: 1.5rem;
}

.app-nav a {
  color: white;
  text-decoration: none;
  opacity: 0.9;
  transition: opacity 0.2s;
}

.app-nav a:hover,
.app-nav a.router-link-active {
  opacity: 1;
  font-weight: 600;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.app-footer {
  text-align: center;
  padding: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
    Cantarell, 'Helvetica Neue', sans-serif;
  background: #f9fafb;
  color: #1f2937;
}
</style>
