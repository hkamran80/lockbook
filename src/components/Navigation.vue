<template>
    <div id="navigation">
        <v-app-bar app color="#13323C" dark>
            <v-toolbar-title>Lockbook</v-toolbar-title>

            <v-spacer></v-spacer>

            <v-btn icon v-if="logged_in">
                <v-icon>mdi-plus</v-icon>
            </v-btn>
            <v-btn icon v-on:click="toggle_dark_mode">
                <v-icon>mdi-theme-light-dark</v-icon>
            </v-btn>
            <v-btn icon v-if="logged_in">
                <v-icon>mdi-logout</v-icon>
            </v-btn>
        </v-app-bar>
    </div>
</template>

<script>
export default {
    name: "Navigation",
    props: ["logged_in"],
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
