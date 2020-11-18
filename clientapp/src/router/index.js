import Vue from 'vue'
import VueRouter from 'vue-router'
import Configure from "../views/Configure";
import Calibrate from "../views/Calibrate";
import SurfConfig from "../views/SurfConfig";
import Home from "../views/Home";

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/configure/:viewId',
    name: 'Configure',
    component: Configure,
    props: true
  },
  {
    path: '/calibrate/:viewId',
    name: 'Calibrate',
    component: Calibrate,
    props: true
  },
    {
    path: '/surf/:viewId',
    name: 'SurfConfig',
    component: SurfConfig,
    props: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
