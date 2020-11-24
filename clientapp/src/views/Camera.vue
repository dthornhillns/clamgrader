<template>
    <v-content>
        <v-layout row wrap align-center fill-height justify-center>
              <v-col cols="12">
                  <v-img max-height="500px" src="/video_feed" contain></v-img>
              </v-col>
                <v-col cols="4">
                    <v-btn v-for="annotation in Object.entries(sizes)" :key="annotation[0]" @click="measure(annotation[0])" class="ma-1">{{annotation[0]}}</v-btn>
                </v-col>
                <v-col cols="2">
                    <v-text-field
                        v-model="customAnnotation"
                        label="Annotation"
                        placeholder="Custom"
                        outlined
                        clearable
                      ></v-text-field>
                    <v-btn @click="measure(customAnnotation)">Measure Custom</v-btn>
                    <v-switch v-model="automaticMeasure" label="Automatic Measure"></v-switch>
                </v-col>
        </v-layout>
    </v-content>
</template>

<script>

export default {
    name: 'Camera',
    data () {
        return {
            config:null,
            sizes:{},
            localViewId:1,
            customAnnotation: "",
            automaticMeasure: true
        }
    },
    components: {
    },
    async mounted() {
        let response = await this.axios.get("/config");
        this.config=response.data;
        this.automaticMeasure = this.config.automaticMeasure;
        response = await this.axios.get("/sizes");
        this.sizes=response.data;
        this.setDisplay();
    },
    watch: {
        automaticMeasure: function (newValue, oldValue) {
            this.setConfig("automaticMeasure", newValue, oldValue);
        }
    },
    methods: {
        async setDisplay() {
            await this.axios.put("/config",{
                showEnhanced: this.localViewId
            });
        },
        async measure(annotation) {
            await this.axios.post("/measure",{
                annotation: annotation
            });
        },
        setConfig(name, newValue, oldValue) {
          if(newValue!=oldValue) {
            let configData={};
            configData[name] = newValue;
            this.axios.put("/config", configData);
          }
        }
    }

}
</script>
