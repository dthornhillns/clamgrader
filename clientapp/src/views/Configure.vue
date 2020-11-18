<template>
    <v-content>
        <v-row>
            <v-col cols="6">
                <v-content>
                    <v-row>
                      <v-col>
                          <v-img max-height="500px" src="/video_feed" contain></v-img>
                      </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="8">
                            <RegionSliders
                                 v-if="config!=null"
                                    :initial-x-min="config.regionOfInterest[0]"
                                    :initial-y-min="config.regionOfInterest[1]"
                                    :initial-x-max="config.regionOfInterest[2]"
                                    :initial-y-max="config.regionOfInterest[3]"
                                title="Area of Interest" configName="regionOfInterest"></RegionSliders>
                        </v-col>
                        <v-col cols="1">
                          <v-btn @click="saveConfig">
                            <v-icon>mdi-content-save</v-icon>
                            Save Config
                        </v-btn>
                      </v-col>
                    </v-row>
                </v-content>
            </v-col>
            <v-col>
                <HSVSliders
                        v-if="config!=null"
                        :initial-hue="config.hue_L"
                        :initial-sat="config.saturation_L"
                        :initial-lev="config.value_L"
                        :initia-threshold="config.threshold_L"
                        title="Low"
                        suffix="_L"
                        class="ma-4">
                </HSVSliders>
                <HSVSliders
                        v-if="config!=null"
                        :initial-hue="config.hue_H"
                        :initial-sat="config.saturation_H"
                        :initial-lev="config.value_H"
                        :initia-threshold="config.threshold_H"
                        title="High"
                        suffix="_H"
                        class="ma-4">
                </HSVSliders>
            </v-col>
        </v-row>
    </v-content>
</template>

<script>
import HSVSliders from "../components/HSVSliders";
import RegionSliders from "../components/RegionSliders";

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
        RegionSliders,
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
        },
        async saveConfig() {
            await this.axios.post("/config");
        }
    }
}
</script>
