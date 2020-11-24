import Vue from 'vue'
import VueRouter from 'vue-router'
import Calibrate from "../views/Calibrate";
import SurfConfig from "../views/SurfConfig";
import Regions from "../views/Regions";
import Home from "../views/Home";
import Targets from "../views/Targets";
import Save from "../views/Save";
import Camera from "../views/Camera";

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/camera',
    name: 'Camera',
    component: Camera
  },
  {
    path: '/regions',
    name: 'Regions',
    component: Regions
  },
  {
    path: '/targets/:viewId',
    name: 'Targets',
    component: Targets,
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
  },
    {
    path: '/save',
    name: 'Save',
    component: Save,
    props: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
