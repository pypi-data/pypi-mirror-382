<template>
 <slot></slot>
</template>

<script>
export default {
  name: 'Stack',
  props: {
    selected_label: Number,  // v-model
    style: {
      type: String,
    },
  },
}
</script>

<style scoped>

</style>
