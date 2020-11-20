<template>
  <v-app id="inspire">
    <v-navigation-drawer
        app
        color="grey lighten-3"
        mini-variant
        permanent
    >
      <v-list>
        <v-list-item to="/"
                     :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-monitor</v-icon>
          </v-list-item-icon>
        </v-list-item>
        <v-list-item to="/regions"
                     :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-shape-square-plus</v-icon>
          </v-list-item-icon>
        </v-list-item>
        <v-list-item to="/targets/3"
                     :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-target</v-icon>
          </v-list-item-icon>
        </v-list-item>
        <v-list-item to="/targets/4"
                     :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-brightness-6</v-icon>
          </v-list-item-icon>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item to="/surf/6"
                     :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-palette-outline</v-icon>
          </v-list-item-icon>
        </v-list-item>
        <v-list-item to="/calibrate/100"
                     :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-ruler-square</v-icon>
          </v-list-item-icon>
        </v-list-item>
        <v-list-item to="/save"
                :ripple="false">
          <v-list-item-icon x-large>
            <v-icon>mdi-content-save</v-icon>
          </v-list-item-icon>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <router-view :key="$route.fullPath"/>
    </v-main>
  </v-app>
</template>


<script>
  export default {
    methods: {
       async saveConfig() {
            await this.axios.post("/config");
        }
    }

  }
</script>