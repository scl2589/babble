import SERVER from '@/api/api'
import axios from 'axios'
import router from '@/router'
// import Swal from 'sweetalert2'


const diaryStore = {
    namespaced: true,
    state: {
        diary: null,
        diaries: null,
        photoDiaries: null,
        diaryId: null,
        comments: null,
        measurments: null,
    },
    getters: {
    },
    mutations: {
        SET_DIARY(state, diary) {
            state.diary = diary
        },
        SET_DIARIES(state, diaries) {
            state.diaries = diaries
        },
        SET_PHOTO_DIARIES(state, photoDiaries) {
            state.photoDiaries = photoDiaries
        },
        SET_COMMENTS(state, comments) {
            state.comments = comments
        },
        SET_MEASUREMENTS(state, measurements) {
            state.measurements = measurements
        }
    },
    actions: {
        createDiary({ rootGetters }, diaryData) {
            axios.post(SERVER.URL + SERVER.ROUTES.diaries, diaryData, rootGetters.config)
                .then(res => {
                    router.push({ name: 'DiaryDetail', params: { diaryId: res.data.id } })
                })
        },
        fetchPhotoDiaries({ rootGetters, commit }) {
            axios.get(SERVER.URL + SERVER.ROUTES.diaries + SERVER.ROUTES.photo , rootGetters.config)
                .then(res => {
                    commit('SET_PHOTO_DIARIES', res.data)
                })
        },
        fetchDiaries({ rootGetters, commit }) {
            axios.get(SERVER.URL + SERVER.ROUTES.diaries, rootGetters.config)
                .then(res => {
                    commit('SET_DIARIES', res.data)
                })

        },
        findDiary({ rootGetters, commit }, diaryId) {
            axios.get(SERVER.URL + SERVER.ROUTES.diaries + diaryId + '/', rootGetters.config)
                .then(res => {
                    commit('SET_DIARY', res.data)
                })
        },
        deleteDiary({ rootGetters }, diaryId) {
            axios.delete(SERVER.URL + SERVER.ROUTES.diaries + diaryId, rootGetters.config)
                .then(() => {
                    router.push({ name: 'DiaryPhoto' })
                })
        },
        updateDiary({ rootGetters }, diaryData) {
            axios.put(SERVER.URL + SERVER.ROUTES.diaries + diaryData.diaryId + '/', diaryData.diaryUpdateData, rootGetters.config)
                .then(() => {
                    router.replace({ name: 'DiaryDetail', params: { diaryId: diaryData.diaryId } })
                })

        },
        fetchComments({ rootGetters, commit }, diaryId) {
            axios.get(SERVER.URL + SERVER.ROUTES.diaries + diaryId + '/comments/', rootGetters.config)
                .then(res => {
                    commit('SET_COMMENTS', res.data)
                })
        },
        createComment({ dispatch, rootGetters }, commentData) {
            axios.post(SERVER.URL + SERVER.ROUTES.diaries + commentData.diaryId + '/comments/', commentData, rootGetters.config)
                .then(() => {
                    dispatch('fetchComments', commentData.diaryId)
                })
        },
        deleteComment({ dispatch, rootGetters }, commentData) {
            axios.delete(SERVER.URL + SERVER.ROUTES.diaries + commentData.diaryId + SERVER.ROUTES.comments + commentData.commentId + '/', rootGetters.config)
                .then(() => {
                    dispatch('fetchComments', commentData.diaryId)
                })
        },
        updateComment({ dispatch, rootGetters }, commentUpdateData) {
            axios.put(SERVER.URL + SERVER.ROUTES.diaries + commentUpdateData.diaryId + SERVER.ROUTES.comments + commentUpdateData.commentId + '/', commentUpdateData, rootGetters.config)
                .then(() => {
                    dispatch('fetchComments', commentUpdateData.diaryId)
                })
        },
        createRecord({ rootGetters }, babyRecord) {
            axios.post(SERVER.URL + SERVER.ROUTES.babies + SERVER.ROUTES.measurements, babyRecord, rootGetters.config)
        },
        updateMeasurement({ rootGetters }, recordData) {
            axios.put(SERVER.URL + SERVER.ROUTES.babies + SERVER.ROUTES.measurements + recordData.measurement_id + '/', recordData.babyRecord, rootGetters.config)
        },
        fetchMeasurements({ rootGetters, commit }) {
            axios.get(SERVER.URL + SERVER.ROUTES.babies + SERVER.ROUTES.measurements, rootGetters.config)
            .then((res) => {
                commit('SET_MEASUREMENTS', res.data)
            })
        },        
    }
}

export default diaryStore