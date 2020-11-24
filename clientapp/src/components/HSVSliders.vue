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
                hue: Math.floor(((this.initialHue)/255)*180),
                sat: Math.floor((this.initialSat/255)*100),
                val: Math.floor((this.initialLev/255)*100),
                threshold: Math.floor((this.initialThreshold/255)*100),
                isMounted: false
            }
        },
      watch: {
        hue: function(newValue, oldValue) {
            let convertedNewVal=Math.floor(((newValue)/180)*255);
            this.setConfig(`${this.prefix}hue${this.suffix}`,convertedNewVal,newValue,oldValue);
          },
        sat: function(newValue, oldValue) {
            let convertedNewVal=Math.floor((newValue/100)*255);
            this.setConfig(`${this.prefix}saturation${this.suffix}`,convertedNewVal,newValue,oldValue);
          },
        val: function(newValue, oldValue) {
            let convertedNewVal=Math.floor((newValue/100)*255);
            this.setConfig(`${this.prefix}value${this.suffix}`,convertedNewVal,newValue,oldValue);
          },
        threshold: function(newValue, oldValue) {
            let convertedNewVal=Math.floor((newValue/100)*255);
            this.setConfig(`${this.prefix}threshold${this.suffix}`,convertedNewVal,newValue,oldValue);
          }
      },
      mounted() {
        this.isMounted = true;
      },
      methods: {
        setConfig(name,convertedNewValue, newValue, oldValue) {
          if(newValue!=oldValue) {
            console.log(`setConfig(${name},${convertedNewValue},${newValue},${oldValue})`)
            let configData={};
            configData[name] = convertedNewValue;
            this.axios.put("/config", configData);
          }
        }
      }
    }
</script>

<style scoped>

</style>