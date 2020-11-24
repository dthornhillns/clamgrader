<template>
     <v-layout row wrap align-center fill-height justify-center>
            <v-card>
                <v-card-title>Save Current Configuration</v-card-title>
                <v-card-text>You are about to save the current configuration that is running on the camera detection software. Do you want to proceed?</v-card-text>
                <v-card-actions>
                    <v-col class="text-right">
                        <v-btn class="red white--text mr-4" @click="cancel()">Cancel</v-btn>
                        <v-btn class="green white--text" @click="saveConfig()">Save</v-btn>
                    </v-col>
                </v-card-actions>
            </v-card>
    </v-layout>
</template>

<script>
    export default {
        name: "Save"
        ,
        methods: {
            async cancel() {
                this.$router.go(-1);
            },
            async saveConfig() {
                await this.axios.post("/config");
                this.$router.go(-1);
            }
        }
    }
</script>

<style scoped>

</style>