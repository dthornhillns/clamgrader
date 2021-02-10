<template>
  <v-card>
    <v-app-bar elevation="0">{{title}}</v-app-bar>
    <v-card-text>
      <v-container fluid>
        <v-row no-gutters>
          <v-col cols="2">
            <v-responsive
              :style="{ background: `hsl(${hue}, 100%, 50%)` }"
              height="50px"
              width="50px"
            ></v-responsive>
          </v-col>
          <v-col cols="8">
            <v-slider
              v-model="hue"
              :max="180"
              :min="-180"
              label="Hue"
              class="align-center ma-2"
              :hint="hue.toString()"
              persistent-hint
              @change="setHue($event)"
            >
            </v-slider>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="2">
            <v-responsive
              :style="{ background: `hsl(${hue}, ${sat}%, 50%)` }"
              height="50px"
              width="50px"
            ></v-responsive>
          </v-col>
          <v-col cols="10">
            <v-slider
              v-model="sat"
              :max="100"
              label="Sat"
              class="align-center ma-2"
              :hint="sat.toString()"
              persistent-hint
              @change="setSat($event)"
            >
            </v-slider>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="2">
            <v-responsive
              :style="{ background: `hsl(${hue}, 0%, ${val}%)` }"
              height="50px"
              width="50px"
            ></v-responsive>
          </v-col>
          <v-col cols="10">
            <v-slider
              v-model="val"
              :max="100"
              label="Lev"
              class="align-right ma-2"
              :hint="val.toString()"
              persistent-hint
              @change="setVal($event)"
            >
            </v-slider>
          </v-col>
        </v-row>
        <v-row v-if="useThreshold" no-gutters>
          <v-col cols="2">
             <v-responsive
              :style="{ background: `hsl(${hue}, 0%, ${threshold}%)` }"
              height="50px"
              width="50px"
            ></v-responsive>
          </v-col>
          <v-col cols="10">
            <v-slider
              v-model="threshold"
              :max="100"
              label="Thr"
              class="align-right ma-2"
              :hint="threshold.toString()"
              persistent-hint
              @change="setThreshold($event)"
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
        name: "HSVSliders",
        props: {
          title: {
            type: String,
            default: ""
          },
          suffix: {
            type: String,
            default: ""
          },
          prefix: {
            type: String,
            default: ""
          },
          useThreshold: {
            type: Boolean,
            default: true
          },
          initialHue: {
            type: Number,
            default: 0.0
          },
          initialSat: {
            type: Number,
            default: 0.0
          },
          initialLev: {
            type: Number,
            default: 0.0
          },
          initialThreshold: {
            type: Number,
            default: 0.0
          }
        },
        data () {
            return {
                hue: 0.0,
                sat: 0.0,
                val: 0.0,
                threshold: 0.0
            }
        },
      mounted() {
          this.hue = Math.floor(((this.initialHue)/255)*180);
          this.sat = Math.floor((this.initialSat/255)*100);
          this.val = Math.floor((this.initialLev/255)*100);
          this.threshold = Math.floor((this.initialThreshold/255)*100);
      },
      methods: {
        setHue(newValue) {
          let convertedNewVal=Math.floor(((newValue)/180)*255);
          this.setConfig(`${this.prefix}hue${this.suffix}`,convertedNewVal,newValue);
        },
        setSat(newValue) {
          let convertedNewVal=Math.floor((newValue/100)*255);
          this.setConfig(`${this.prefix}saturation${this.suffix}`,convertedNewVal,newValue);
        },
        setVal(newValue) {
          let convertedNewVal=Math.floor((newValue/100)*255);
          this.setConfig(`${this.prefix}value${this.suffix}`,convertedNewVal,newValue);
        },
        setThreshold(newValue) {
          let convertedNewVal=Math.floor((newValue/100)*255);
          this.setConfig(`${this.prefix}threshold${this.suffix}`,convertedNewVal,newValue);
        },
        async setConfig(name,convertedNewValue, newValue) {
          console.log(`setConfig(${name},${convertedNewValue},${newValue})`)
          let configData={};
          configData[name] = convertedNewValue;
          await this.axios.put("/config", configData);
        }
      }
    }
</script>

<style scoped>

</style>