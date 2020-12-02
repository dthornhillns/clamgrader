<template>
    <v-content>
        <v-layout row wrap align-center fill-height justify-center>
              <v-col cols="12">
                  <v-img max-height="500px" src="/video_feed" contain></v-img>
              </v-col>
                <v-col cols="4">
                    <HSVSliders
                        v-if="config!=null"
                        :initial-hue="config.surf_hue_L"
                        :initial-sat="config.surf_saturation_L"
                        :initial-lev="config.surf_value_L"
                        :initial-threshold="config.surf_threshold_L"
                        title="Low" prefix="surf_" suffix="_L"
                        v-bind:use-threshold="false"
                    class="ma-4"/>
                </v-col>
                <v-col cols="4">
                    <HSVSliders
                        v-if="config!=null"
                        :initial-hue="config.surf_hue_H"
                        :initial-sat="config.surf_saturation_H"
                        :initial-lev="config.surf_value_H"
                        :initial-threshold="config.surf_threshold_H"
                        title="High" prefix="surf_" suffix="_H"
                        v-bind:use-threshold="false"
                        class="ma-4"/>
                </v-col>
                <v-col cols="2">
                    <v-card class="ma-4 pa-0">
                        <v-app-bar elevation="0">Red Threshold</v-app-bar>
                        <v-card-subtitle>{{this.percentRed}}%</v-card-subtitle>
                        <v-card-text>
                            <v-slider
                              v-model="percentRed"
                              :max="100"
                              :min="0"
                              label="Red%"
                              class="align-center ma-2"
                              style="height:180px"
                              hint="xyz"
                              persistent-hint
                              vertical
                            >
                            </v-slider>
                        </v-card-text>
                    </v-card>
            </v-col>
        </v-layout>
    </v-content>
</template>

<script>
import HSVSliders from "../components/HSVSliders";

export default {
    name: 'SurfConfig',
    components: {
        HSVSliders
    },
    data () {
        return {
            config:null,
            localViewId:6,
            percentRed:0
        }
    },
    async mounted() {
        let response = await this.axios.get("/config");
        this.config=response.data;
        this.percentRed = this.config.surf_red_percent;
        this.setDisplay();
    },
    watch: {
        percentRed: function(newVal, oldVal) {
            this.setConfig("surf_red_percent",newVal, oldVal)
        }
    },
    methods: {
        async setDisplay() {
            await this.axios.put("/config",{
                showEnhanced: this.localViewId
            });
        },
        setConfig(name, newValue, oldValue) {
          if(newValue!=oldValue) {
            console.log(`setConfig(${name},${newValue},${oldValue})`)
            let configData={};
            configData[name] = newValue;
            this.axios.put("/config", configData);
          }
        }
    }
}
</script>
