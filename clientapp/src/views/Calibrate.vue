<template>
    <v-content>
        <v-layout row wrap align-center fill-height justify-center>
            <v-col cols="12">
              <v-img max-height="500px" src="/video_feed" contain></v-img>
            </v-col>
            <v-col cols="4">
                <RegionSliders v-if="config!=null"
                               :initial-x-min="config.calibrationBox[0]"
                               :initial-x-max="config.calibrationBox[2]"
                               :initial-y-min="config.calibrationBox[1]"
                               :initial-y-max="config.calibrationBox[3]"
                               title="Calibration Area"
                               configName="calibrationBox"/>
            </v-col>
        </v-layout>
    </v-content>
</template>

<script>
import RegionSliders from "../components/RegionSliders";

export default {
    name: 'Calibrate',
    components: {
      RegionSliders
    },
    data () {
        return {
            config:null,
            localViewId:parseInt(this.viewId)
        }
    },
    props: {
        viewId : String
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
