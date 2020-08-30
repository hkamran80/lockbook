<template>
    <div class="home">
        <v-subheader inset>
            2020
        </v-subheader>
        <v-divider />
        <div id="entries">
            <v-card class="mx-auto" min-width="250" max-width="250" outlined>
                <v-list-item two-line>
                    <v-list-item-content>
                        <v-list-item-title class="headline mb-1">
                            June 22
                        </v-list-item-title>
                        <v-list-item-subtitle>1 entry</v-list-item-subtitle>
                    </v-list-item-content>
                </v-list-item>
            </v-card>
        </div>
    </div>
</template>

<script>
export default {
    name: "Home"
};
</script>
<style scoped>
hr.v-divider {
    margin-bottom: 25px;
}
div#entries {
    text-align: left;
}
</style>
