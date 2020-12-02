<template>
    <v-content>
        <v-layout row wrap align-center fill-height justify-center>
              <v-col cols="12">
                  <v-img max-height="500px" src="/video_feed" contain></v-img>
              </v-col>
                <v-col>
                    <HSVSliders
                            v-if="config!=null"
                            :initial-hue="config.hue_L"
                            :initial-sat="config.saturation_L"
                            :initial-lev="config.value_L"
                            :initial-threshold="config.threshold_L"
                            title="Low"
                            suffix="_L"
                            class="ma-4">
                    </HSVSliders>
                </v-col>
                <v-col>
                    <HSVSliders
                            v-if="config!=null"
                            :initial-hue="config.hue_H"
                            :initial-sat="config.saturation_H"
                            :initial-lev="config.value_H"
                            :initial-threshold="config.threshold_H"
                            title="High"
                            suffix="_H"
                            class="ma-4">
                    </HSVSliders>
                </v-col>
        </v-layout>
    </v-content>
</template>

<script>
import HSVSliders from "../components/HSVSliders";

export default {
    name: 'Configure',
    data () {
        return {
            config:null,
            localViewId:parseInt(this.viewId)
        }
    },
    props: {
        viewId : String
    },
    components: {
        HSVSliders
    },
    async mounted() {
        let response = await this.axios.get("/config");
        this.config=response.data;
        this.setDisplay();
    },
    methods: {
        async setDisplay() {
            await this.axios.put("/config",{
                showEnhanced: this.localViewId
            });
        }
    }
}
</script>
