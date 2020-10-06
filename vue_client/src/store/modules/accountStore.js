import SERVER from '@/api/api'
import axios from 'axios'
import router from '@/router'
import Swal from 'sweetalert2'


const accountStore = {
    namespaced: true,
    state: {

    },
    getters: {

    },
    mutations: {

    },
    actions: {
        postAuthData1({ rootState, commit } , info) {
            axios.post(SERVER.URL + SERVER.ROUTES.signup, info.data)
              .then(res => {
                commit('SET_TOKEN', res.data.key, { root: true })
                const Toast = Swal.mixin({
                  toast: true,
                  position: 'top-end',
                  showConfirmButton: false,
                  timer: 2000,
                  timerProgressBar: true,
                  onOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                    }
                 })
                 Toast.fire({
                  icon: 'success',
                  title: "회원가입에 성공하였습니다."
                })
                if (rootState.invitationToken) {
                  console.log(rootState.invitationToken)
                  router.push({ name: "InvitationConfirm", params: { token: rootState.invitationToken }})
                } else {
                  router.push({name: 'RegisterBaby'})
                }
              })

              .catch(err => {
                console.log(err.response)
                const Toast = Swal.mixin({
                  toast: true,
                  position: 'top-end',
                  showConfirmButton: false,
                  timer: 3000,
                  timerProgressBar: false,
                  onOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                    }
                 })
                 Toast.fire({
                  icon: 'error',
                  title: "아이디와 비밀번호를 확인해주세요"
                })
              })
          },
        postAuthData2({ rootState, commit, dispatch }, info) {
            axios.post(SERVER.URL + SERVER.ROUTES.login, info.data)
              .then(res => {
                commit('SET_TOKEN', res.data.key, { root: true })
                const Toast = Swal.mixin({
                  toast: true,
                  position: 'top-end',
                  showConfirmButton: false,
                  timer: 2000,
                  timerProgressBar: true,
                  onOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                    }
                 })
                 Toast.fire({
                  icon: 'success',
                  title: "로그인에 성공하였습니다."
                })
                dispatch('findMyAccount', null, { root: true })
                // dispatch('findBaby', rootState.myaccount.current_baby, { root: true })
                if (rootState.invitationToken) {
                  console.log(rootState.invitationToken)
                  router.push({ name: "InvitationConfirm", params: { token: rootState.invitationToken }})
                } else {
                router.push({name: 'PhotoList'})
                }
              })
              .catch(() => {
                const Toast = Swal.mixin({
                  toast: true,
                  position: 'top-end',
                  showConfirmButton: false,
                  timer: 3000,
                  timerProgressBar: false,
                  onOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                    }
                 })
                 Toast.fire({
                  icon: 'error',
                  title: "아이디와 비밀번호를 확인해주세요"
                })
              })
          },
        // login
        login({ dispatch }, loginData) {
            const info = {
              data: loginData,
              location: SERVER.ROUTES.login,
            }
            dispatch('postAuthData2', info)
        },
        signup({ dispatch }, signupData) {
          const info = {
            data: signupData,
            location: SERVER.ROUTES.signup,
          }
          dispatch('postAuthData1', info)
        },
        enrollBaby({ rootGetters, dispatch }, enrollData) {
          console.log(enrollData)
          axios.post(SERVER.URL + SERVER.ROUTES.babies, enrollData, rootGetters.config)
            .then(res => {
              console.log(res)
              dispatch('findMyAccount', null, { root: true })
              // dispatch('findBaby', rootState.myaccount.current_baby, { root: true })
              router.push({ name: 'PhotoList'})
            })
            .catch(err => {
              console.error(err)
            })
        },
        socialLogin({ commit, dispatch, rootState }, userInfo) {
          axios.post(SERVER.URL + SERVER.ROUTES.social, userInfo)
            .then(res => {
              commit('SET_TOKEN', res.data.key, { root: true });
              dispatch('findMyAccount', null, { root: true })
              const Toast = Swal.mixin({
                toast: true,
                position: "top-end",
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                onOpen: (toast) => {
                  toast.addEventListener("mouseenter", Swal.stopTimer);
                  toast.addEventListener("mouseleave", Swal.resumeTimer);
                },
              });
              Toast.fire({
                icon: "success",
                title: "로그인에 성공하였습니다.",
              });
              if (res.data.state === 'login') {
                if (rootState.invitationToken) {
                  router.push({ name: "InvitationConfirm", params: { token: rootState.invitationToken }})
                } else {
                  router.push({name: 'PhotoList'});
                }
              } else if (res.data.state === 'signup') {
                if (rootState.invitationToken) {
                  router.push({ name: "InvitationConfirm", params: { token: rootState.invitationToken }})
                } else {
                  router.push({name: 'RegisterBaby'})
                } 
              }
            })
            .catch((err) => {
              console.log(err)
              const Toast = Swal.mixin({
                toast: true,
                position: "top-end",
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true,
                onOpen: (toast) => {
                  toast.addEventListener("mouseenter", Swal.stopTimer);
                  toast.addEventListener("mouseleave", Swal.resumeTimer);
                },
              });
              Toast.fire({
                icon: "error",
                title: err.response.data.message,
              });
            });
        },
        changePassword({ rootGetters }, passwordData) {
          axios.put(SERVER.URL + SERVER.ROUTES.password + 'change/', passwordData, rootGetters.config)
            .then(res => {
              console.log(res)
              router.go(0)
            })
            .catch(err => {
              console.log(err)
          })
        },
    }
}

export default accountStore