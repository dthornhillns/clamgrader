<template>
    <v-content  class="ma-0 pa-0">
        <v-img max-height="900px" src="/video_feed" contain></v-img>
    </v-content>
</template>

<script>

export default {
    name: 'Home',
    props: {
        viewId : String
    },
    components: {
    },
    async created() {
      await this.axios.put("/config",{
                showEnhanced: 0
            });
    }
}
</script>
