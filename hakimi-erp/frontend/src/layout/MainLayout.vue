<template>
  <div class="main-layout">
    <Sidebar />
    <div class="main-content">
      <TopBar />
      <div class="page-content">
        <router-view />
      </div>
      <FooterBar />
    </div>
    <ChatWidget />
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import FooterBar from './FooterBar.vue'
import ChatWidget from '@/components/ChatWidget.vue'
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  min-width: 1280px;
  overflow: hidden;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.page-content {
  flex: 1;
  overflow-y: auto;
  background-color: #FBFADA;
}
</style>
