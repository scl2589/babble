import Vue from 'vue'
import Vuex from 'vuex'

import accountStore from '@/store/modules/accountStore'
import diaryStore from '@/store/modules/diaryStore'
import photoStore from '@/store/modules/photoStore'
import settingStore from '@/store/modules/settingStore'

import cookies from 'vue-cookies'
import axios from 'axios'
import SERVER from '@/api/api'
import Swal from 'sweetalert2'
import router from '@/router'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    authToken: cookies.get('auth-token'),
    myaccount: null,
    currentBaby: null,
    babbleboxes: null,
  },
  getters: {
    config: state => ({ headers: { Authorization: `Token ${state.authToken}`}}),
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.authToken = token
      cookies.set('auth-token', token)
    },
    SET_MYACCOUNT(state, user) {
      state.myaccount = user
    },
    SET_BABY(state, baby) {
      state.currentBaby = baby
    },
    SET_BABBLEBOX(state, babbleboxes) {
      state.babbleboxes = babbleboxes
    }
  },
  actions: {
    findBaby({ commit, getters }, baby_id) {
      axios.get(SERVER.URL + SERVER.ROUTES.babies + baby_id, getters.config)
        .then(res => {
          console.log(res)
          commit('SET_BABY', res.data)
        })
        .catch(err => {
          console.log(err)
        })
    },
    findMyAccount({ commit, getters}) {
      axios.get(SERVER.URL + SERVER.ROUTES.myaccount, getters.config)
        .then(res => {
          commit('SET_MYACCOUNT', res.data)
        })
        .catch(err => {
          console.log(err)
        })
    },
    logout({ commit, getters }) {
      axios.post(SERVER.URL + SERVER.ROUTES.logout, null, getters.config)
        .then(() => {
          commit('SET_TOKEN', null)
          cookies.remove('auth-token')
          const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            onOpen: (toast) => {
              toast.addEventListener('mouseenter', Swal.stopTimer)
              toast.addEventListener('mouseleave', Swal.resumeTimer)
              }
          })
          Toast.fire({
            icon: 'success',
            title: '로그아웃되었습니다.'
          })
          router.push({ name: 'Login' })
        })
        .catch(err => {
          console.log(err)
        })
    },
    fetchBabbleBox({ commit, getters }) {
      axios.get(SERVER.URL + SERVER.ROUTES.babies + SERVER.ROUTES.babblebox, getters.config)
        .then(res => {
          commit('SET_BABBLEBOX', res.data)
        })
        .catch(err => {
          console.log(err)
        })
    },
    accessBabbleBox({ dispatch, getters }, accessData) {
      axios.post(SERVER.URL + SERVER.ROUTES.access, accessData, getters.config)
        .then(() => {
          dispatch('findBaby',accessData.baby)
          router.push({ name: 'PhotoList' })
        })
        .catch(err => {
          console.log(err)
        })
    }
  },
  modules: {
    accountStore: accountStore,
    diaryStore: diaryStore,
    photoStore: photoStore,
    settingStore: settingStore,
  }
})

// save our state (isPanel open or not) 
export const store = Vue.observable({
  isNavOpen: false
});

// We call toggleNav anywhere we need it in our app
export const mutations = {
  setIsNavOpen(yesno) {
    store.isNavOpen = yesno;
  },
  toggleNav() {
      store.isNavOpen = !store.isNavOpen
  }
};