<template>
    <v-card width="600px">
      <v-app-bar elevation="0">{{title}}</v-app-bar>
        <v-card-text>
          <v-container fluid>
            <v-row no-gutters>
              <v-col cols="2">
                <v-slider
                  v-model="yMin"
                  :max="100"
                  :min="0"
                  label="Y-Min"
                  class="align-center ma-2"
                  :hint="yMin.toString()"
                  vertical
                  persistent-hint
                  height="100px"
                  @change="onYMin($event)"
                >
                </v-slider>
              </v-col>
                <v-col cols="2">
                  <v-slider
                  v-model="yMax"
                  :max="100"
                  :min="0"
                  label="Y-Max"
                  class="align-center ma-2"
                  :hint="yMax.toString()"
                  vertical
                  persistent-hint
                  height="100px"
                  @change="onYMax($event)"
                >
                </v-slider>
              </v-col>
                <v-col cols="8">
                  <v-slider
                  v-model="xMax"
                  :max="100"
                  :min="0"
                  label="X-Max"
                  class="align-center ma-2"
                  :hint="xMax.toString()"
                  persistent-hint
                  @change="onXMax($event)"
                >
                </v-slider>
                     <v-slider
                  v-model="xMin"
                  :max="100"
                  :min="0"
                  label="X-Min"
                  class="align-center ma-2"
                  :hint="xMin.toString()"
                  persistent-hint
                  @change="onXMin($event)"
                >
                </v-slider>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
    </v-card>
</template>

<script>
    export default {
      name: "RegionSliders",
      data () {
          return {
              xMin: 0.0,
              yMin: 100.0,
              xMax: 0.0,
              yMax: 100.0
          }
      },
      props: {
        configName: String,
        title: String,
        initialXMin: {
          type: Number
        },
        initialXMax: {
          type: Number
        },
        initialYMin: {
          type: Number
        },
        initialYMax: {
          type: Number
        }
      },
      mounted() {
        this.xMin = this.initialXMin*100.0,
        this.yMin = 100.0-(this.initialYMin*100.0),
        this.xMax = this.initialXMax*100.0,
        this.yMax = 100.0-(this.initialYMax*100.0),
        console.log(`region(${this.xMin},${this.yMin},${this.xMax},${this.yMax})`)
      },
      methods: {
          onYMin(newValue) {
            this.setBox([this.xMin/100.0,(100-newValue)/100.0,this.xMax/100.0,(100-this.yMax)/100.0]);
          },
          onYMax(newValue) {
            this.setBox([this.xMin/100.0,(100-this.yMin)/100.0,this.xMax/100.0,(100-newValue)/100.0]);
          },
          onXMin(newValue) {
            this.setBox([newValue/100.0,(100-this.yMin)/100.0,this.xMax/100.0,(100-this.yMax)/100.0]);
          },
          onXMax(newValue) {
            this.setBox([this.xMin/100.0,(100-this.yMin)/100.0,newValue/100.0,(100-this.yMax)/100.0]);
          },
          setBox(boxValues) {
            console.log(`setbox(${boxValues})`)
            let configData={};
            configData[this.configName] = boxValues;
            this.axios.put("/config", configData);
          }
      }
    }
</script>

<style scoped>

</style>