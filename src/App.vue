<template>
    <v-app>
        <Navigation logged-in="false"></Navigation>

        <v-main>
            <v-container fluid>
                <router-view />
            </v-container>
        </v-main>
        <v-footer>
            <router-link to="/">
                Login/Register
            </router-link>
            <v-divider inset vertical />
            <router-link to="/home">
                Home
            </router-link>
            <v-divider inset vertical />
            <router-link to="/account">
                Account
            </router-link>
        </v-footer>
    </v-app>
</template>

<script>
import Navigation from "./components/Navigation";

export default {
    name: "App",
    components: {
        Navigation
    },
    methods: {
        toggle_dark_mode: function() {
            this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
            localStorage.setItem(
                "dark_theme",
                this.$vuetify.theme.dark.toString()
            );
        }
    },
    mounted() {
        const theme = localStorage.getItem("dark_theme");
        if (theme) {
            // deepcode ignore UseStrictEquality: Loaded as a String, not a Boolean
            if (theme == "true") {
                this.$vuetify.theme.dark = true;
            } else {
                this.$vuetify.theme.dark = false;
            }
        } else if (
            window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: dark)").matches
        ) {
            this.$vuetify.theme.dark = true;
            localStorage.setItem(
                "dark_theme",
                this.$vuetify.theme.dark.toString()
            );
        }
    }
};
</script>
