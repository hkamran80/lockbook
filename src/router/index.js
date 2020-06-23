import Vue from "vue";
import VueRouter from "vue-router";
import LoginRegister from "../views/LoginRegister.vue";

Vue.use(VueRouter);

const routes = [
    {
        path: "/",
        name: "LoginRegister",
        component: LoginRegister
    },
    {
        path: "/home",
        name: "Home",
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () =>
            import(/* webpackChunkName: "home" */ "../views/Home.vue")
    },
    {
        path: "/account",
        name: "Account",
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () =>
            import(/* webpackChunkName: "account" */ "../views/Account.vue")
    }
];

const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes
});

export default router;
