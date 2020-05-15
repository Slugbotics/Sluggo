// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        username: username,
        tickets: [],
        add_ticket_text:  "",
        add_ticket_title:  "",
        selected_priority: "",
        is_add_empty: false,
        page: 'list',

        // Complete.
    };

    // Add here the various functions you need.
    app.add_ticket = () => {
        let error = false;
        if(app.vue.add_ticket_text.trim().length === 0) {
            app.vue.is_add_empty = true;
            error = true;
        }
        if(!error) {
            app.perform_insertion();
        }
    };

    app.perform_insertion = () => {

        axios.post(add_tickets_url, {
            ticket_text: app.vue.add_ticket_text,
            ticket_title: app.vue.add_ticket_title,
            ticket_status: "in progress",
            ticket_priority: app.vue.selected_priority
        }).then((result) => {
            app.vue.tickets.unshift({
                id: result.data.id,
                ticket_text: app.vue.add_ticket_text,
                ticket_title: app.vue.add_ticket_title,
                ticket_author: app.vue.username,
                ticket_status: "in progress",
                ticket_priority: app.vue.selected_priority
            });
            app.reindex(app.vue.tickets);
            app.reset_input();
            app.goto('list');
        });
    };

    app.reset_input = () => {
        app.vue.add_ticket_text = "";
        app.vue.is_add_empty = false;
    }

    app.check_ticket_text = () => {
        app.vue.is_add_empty = (app.vue.add_ticket_text.trim().length === 0);
    };

    app.delete_ticket = (ticket_idx) => {
        let t = app.vue.tickets[ticket_idx];

        axios.post(delete_tickets_url, {id:t.id}).then(() => {
            app.vue.tickets.splice(ticket_idx, 1);
            app.reindex(app.vue.tickets);
        })
    };


    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
        }
        return a;
    };

    app.goto = (destination) => {
        app.vue.page = destination;
        // app.vue.add_post_text = "";
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        // Complete.
        goto: app.goto,
        add_ticket: app.add_ticket,
        check_ticket_text: app.check_ticket_text,
        delete_ticket: app.delete_ticket,

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(get_tickets_url).then((result) => {
            let tickets = result.data.tickets;
            app.reindex(tickets);
            app.vue.tickets = tickets;

        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
