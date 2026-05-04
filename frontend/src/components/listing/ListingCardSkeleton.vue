<template>
  <div class="card-skeleton">
    <div class="card-skeleton__image skeleton" />
    <div class="card-skeleton__body">
      <div class="skeleton" style="width: 60px; height: 12px; border-radius: 4px;" />
      <div class="skeleton" style="width: 100%; height: 16px; border-radius: 4px;" />
      <div class="skeleton" style="width: 75%; height: 16px; border-radius: 4px;" />
      <div class="skeleton" style="width: 40%; height: 12px; border-radius: 4px;" />
      <div class="card-skeleton__footer">
        <div class="skeleton" style="width: 90px; height: 20px; border-radius: 4px;" />
        <div class="skeleton" style="width: 40px; height: 14px; border-radius: 4px;" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-skeleton {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.card-skeleton__image {
  aspect-ratio: 4/3;
  width: 100%;
}
.card-skeleton__body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.card-skeleton__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  margin-top: 4px;
}
</style>
