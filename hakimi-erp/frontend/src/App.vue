<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
  font-size: 13px;
  color: var(--app-text);
  background: var(--app-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background-color 0.25s ease, color 0.25s ease;
}

#app {
  height: 100%;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(173, 188, 159, 0.45); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(173, 188, 159, 0.7); }

::selection {
  background-color: rgba(67, 104, 80, 0.18);
  color: #12372A;
}

/* Toast - centered notification style per UX spec */
.hakimi-toast-center.el-message {
  top: 50% !important;
  bottom: auto !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  min-width: 320px;
  max-width: 560px;
  padding: 12px 18px;
  border-radius: 10px;
  background: #12372A;
  border: 1px solid rgba(67, 104, 80, 0.3);
  box-shadow: 0 10px 30px rgba(18, 55, 42, 0.26);
}

.hakimi-toast-center.el-message .el-message__content {
  color: #FBFADA;
  font-size: 13px;
  font-weight: 500;
}

.hakimi-toast-center.el-message .el-message__icon {
  color: #FBFADA;
}

.hakimi-toast-center.el-message--success {
  background: #436850;
  border-color: rgba(67, 104, 80, 0.5);
}

.hakimi-toast-center.el-message--error {
  background: #D9534F;
  border-color: rgba(217, 83, 79, 0.5);
}

.hakimi-toast-center.el-message--warning {
  background: #F0AD4E;
  border-color: rgba(240, 173, 78, 0.5);
}

.el-overlay.is-message-box {
  background-color: rgba(18, 55, 42, 0.3);
  backdrop-filter: blur(4px);
}

.hakimi-confirm-dialog,
.hakimi-alert-dialog,
.hakimi-prompt-dialog {
  width: 480px;
  max-width: calc(100vw - 32px);
  padding: 0;
  background: linear-gradient(145deg, #fdfce8, #f7f5d1);
  border: 1px solid rgba(173, 188, 159, 0.2);
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(18, 55, 42, 0.22);
  overflow: hidden;
}

.hakimi-confirm-dialog .el-message-box__header,
.hakimi-alert-dialog .el-message-box__header,
.hakimi-prompt-dialog .el-message-box__header {
  position: relative;
  display: flex;
  align-items: center;
  padding: 20px 24px 14px;
  border-bottom: 1px solid rgba(173, 188, 159, 0.12);
}

.hakimi-confirm-dialog .el-message-box__title,
.hakimi-alert-dialog .el-message-box__title,
.hakimi-prompt-dialog .el-message-box__title {
  color: #436850;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.3;
}

.hakimi-confirm-dialog .el-message-box__headerbtn,
.hakimi-alert-dialog .el-message-box__headerbtn,
.hakimi-prompt-dialog .el-message-box__headerbtn {
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
}

.hakimi-confirm-dialog .el-message-box__headerbtn .el-message-box__close,
.hakimi-alert-dialog .el-message-box__headerbtn .el-message-box__close,
.hakimi-prompt-dialog .el-message-box__headerbtn .el-message-box__close {
  color: rgba(18, 55, 42, 0.35);
}

.hakimi-confirm-dialog .el-message-box__headerbtn:hover .el-message-box__close,
.hakimi-alert-dialog .el-message-box__headerbtn:hover .el-message-box__close,
.hakimi-prompt-dialog .el-message-box__headerbtn:hover .el-message-box__close {
  color: #D9534F;
}

.hakimi-confirm-dialog .el-message-box__content,
.hakimi-alert-dialog .el-message-box__content,
.hakimi-prompt-dialog .el-message-box__content {
  padding: 20px 24px;
  color: #12372A;
  font-size: 14px;
}

.hakimi-confirm-dialog .el-message-box__container,
.hakimi-alert-dialog .el-message-box__container,
.hakimi-prompt-dialog .el-message-box__container {
  display: block;
  padding: 0;
}

.hakimi-confirm-dialog .el-message-box__status,
.hakimi-alert-dialog .el-message-box__status,
.hakimi-prompt-dialog .el-message-box__status {
  display: none;
}

.hakimi-confirm-dialog .el-message-box__message,
.hakimi-alert-dialog .el-message-box__message,
.hakimi-prompt-dialog .el-message-box__message {
  color: #12372A;
  font-size: 14px;
  line-height: 1.6;
}

.hakimi-prompt-dialog .el-message-box__input {
  padding-top: 16px;
}

.hakimi-prompt-dialog .el-message-box__input .el-input__inner {
  height: 38px;
  border: 1px solid rgba(173, 188, 159, 0.4);
  border-radius: 8px;
  color: #12372A;
  font-family: inherit;
}

.hakimi-prompt-dialog .el-message-box__input .el-input__inner:focus {
  border-color: #436850;
  box-shadow: 0 0 0 3px rgba(67, 104, 80, 0.08);
}

.hakimi-confirm-dialog .el-message-box__btns,
.hakimi-alert-dialog .el-message-box__btns,
.hakimi-prompt-dialog .el-message-box__btns {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 24px;
  background: rgba(251, 250, 218, 0.25);
  border-top: 1px solid rgba(173, 188, 159, 0.1);
}

.hakimi-confirm-dialog .el-button,
.hakimi-alert-dialog .el-button,
.hakimi-prompt-dialog .el-button {
  height: 38px;
  margin-left: 0;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: 600;
}

.hakimi-confirm-dialog .el-button--primary,
.hakimi-alert-dialog .el-button--primary,
.hakimi-prompt-dialog .el-button--primary {
  background: linear-gradient(135deg, #436850, #365440);
  border-color: #436850;
  color: #FBFADA;
  box-shadow: 0 4px 12px rgba(67, 104, 80, 0.2);
}

.hakimi-confirm-dialog .el-button--primary:hover,
.hakimi-alert-dialog .el-button--primary:hover,
.hakimi-prompt-dialog .el-button--primary:hover {
  background: #365440;
  border-color: #365440;
  color: #FBFADA;
}

.hakimi-confirm-dialog .el-button:not(.el-button--primary),
.hakimi-alert-dialog .el-button:not(.el-button--primary),
.hakimi-prompt-dialog .el-button:not(.el-button--primary) {
  background: rgba(173, 188, 159, 0.2);
  border-color: rgba(173, 188, 159, 0.3);
  color: #436850;
}

.hakimi-confirm-dialog .el-button:not(.el-button--primary):hover,
.hakimi-alert-dialog .el-button:not(.el-button--primary):hover,
.hakimi-prompt-dialog .el-button:not(.el-button--primary):hover {
  background: rgba(173, 188, 159, 0.3);
  border-color: #436850;
  color: #436850;
}
</style>
