<template>
    <v-content>
        <v-layout row wrap align-center fill-height justify-center>
              <v-col cols="12">
                  <v-img max-height="500px" src="/video_feed" contain></v-img>
              </v-col>
                <v-col>
                    <v-layout align-center justify-center>
                        <RegionSliders
                                     v-if="config!=null"
                                        :initial-x-min="config.regionOfInterest[0]"
                                        :initial-y-min="config.regionOfInterest[1]"
                                        :initial-x-max="config.regionOfInterest[2]"
                                        :initial-y-max="config.regionOfInterest[3]"
                                    title="Area of Interest" configName="regionOfInterest"></RegionSliders>
                    </v-layout>
                </v-col>
                <v-col>
                    <v-layout align-center justify-center>
                        <RegionSliders
                                     v-if="config!=null"
                                        :initial-x-min="config.regionOfMeasurement[0]"
                                        :initial-y-min="config.regionOfMeasurement[1]"
                                        :initial-x-max="config.regionOfMeasurement[2]"
                                        :initial-y-max="config.regionOfMeasurement[3]"
                                    title="Area of Measurement" configName="regionOfMeasurement"></RegionSliders>
                    </v-layout>
                </v-col>
        </v-layout>
    </v-content>
</template>

<script>
import RegionSliders from "../components/RegionSliders";

export default {
    name: 'Regions',
    data () {
        return {
            config:null,
            localViewId:1
        }
    },
    components: {
        RegionSliders
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
