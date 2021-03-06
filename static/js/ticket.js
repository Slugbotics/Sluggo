/*
    ticket.js - JavaScript code for tickets page
    part of Sluggo, a free and open source issue tracker
    Copyright (c) 2020 Slugbotics - see git repository history for individual committers

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at https://mozilla.org/MPL/2.0/.
*/

// vanilla javascript for tracking if click is registered outside of object

Vue.directive('click-outside', {
    bind(el, binding, vnode) {
        var vm = vnode.context;
        var callback = binding.value;

        el.clickOutsideEvent = function (event){
            if (!(el === event.target || el.contains(event.target))) {
                return callback.call(vm, event);
            }
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
    },
    unbind(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent);
    }
});


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
        master: [],
        page: 'list',
        showModal: false,
        selectedIdx: false,
        submitCallback: null,
        cancelCallback: null,
        searchText: "",
        searchTag: "",
        searchStatus: "",
        selected_ticket: {},
        tagList: ["", "hello", "there"],
        tagString: "",
        placeHolder: "tag",
        ticket_tags: [],
        get_tags: "",
        selected_tags: [],
        shit: true,
        selected_progress: [],
        selected_users: [],
        status_strings: ['Complete', 'In Progress', 'Not Started'],
        status_map: {
            'Complete': 3,
            'In Progress': 2,
            'Not Started': 1
        },
        project_users: [],
        current_status: "",
        pinned_tickets: [],
        approved: approved == "True"
        // Complete.
    };

    // Add here the various functions you need.
    app.add_ticket = () => {
        // this initializes the modal to handle adding
        app.data.submitCallback = app.submit_add;
        app.data.selected_ticket = {show: false, tag_list: [], ticket_status: "To do", ticket_priority: "low"};
        app.data.showModal = true;
    };

    app.submit_add = () => {
        let error = false;
        let ticket = app.data.selected_ticket;
        // validation *should* be done by the modal
        axios.post(add_tickets_url, ticket).then((response) => {
            console.log(response.data.ticket);
            app.data.tickets.unshift(response.data.ticket);
            app.reindex(app.data.tickets);
            app.data.showModal = false;
            app.data.submitCallback = null;
        }).catch((error) => {
            console.log(error);
        });
    };

    app.close_modal = () => {
        app.data.selectedIdx = false;
        app.data.showModal = false;
    };


    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
            p.show = false;
            if(p.started !== null) {
                if(p.completed !== null)
                    p.status = 3;
                else
                    p.status = 2;
            } else {
                p.status = 1;
            }
        }
        return a;
    };

    app.filter_list = () => {
        app.data.tickets = app.data.master.filter((ticket) => {
            // check if the tag lists match the currently selected tags
            if(!app.data.selected_tags.map(e => e.tag_name).filter(x => ticket.tag_list.map(e => e.tag_name).includes(x)).length > 0 &&
                app.data.selected_tags.length > 0){
                return false;
            }

            // check if the ticket is completed
            let status = app.data.selected_progress.map(x => app.data.status_map[x]);
            if(!status.includes(ticket.status) &&
                app.data.selected_progress.length > 0) {
                return false;
            }

            // check if the assigned user is correct
            if(!app.data.selected_users.map(e => e.user).includes(ticket.assigned_user) &&
                app.data.selected_users.length > 0) return false;

            if((ticket.ticket_text && // see if the ticket_text is null before comparing it to the search text
                ticket.ticket_text.toLowerCase().includes(app.data.searchText.trim().toLowerCase()) ) ||
               ticket.ticket_title.toLowerCase().includes(app.data.searchText.trim().toLowerCase()))
                return true;

            return false;

        });
    };

    app.redirect = (id) => {

        // Only allow approved users to see ticket details.
        if(app.data.approved === false) {
            return;
        }

        window.location.href = ticket_details_url + '/' + id;
    };

    app.register = (shit) => {
        console.log(shit);
    };
    app.refreshPinGraphics = () => {
        for(ticket of app.data.tickets) {
            if(app.data.pinned_tickets.includes(ticket.id)) {
                Vue.set(ticket, "pinned", true);
            } else {
                Vue.set(ticket, "pinned", false);
            }
        }
    };

    app.togglePinStatus = (ticket) => {
        let ticketID = ticket.id;

        // make a server call
        axios.post(pin_ticket_url, {
            ticket_id: ticketID
        }).then((result) => {
            Vue.set(ticket, "pinned", !ticket.pinned);
        })
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        // Complete.
        add_ticket: app.add_ticket,
        close_modal: app.close_modal,
        submit_add: app.submit_add,
        filter_list: app.filter_list,
        redirect: app.redirect,
        register: app.register,
        togglePinStatus: app.togglePinStatus,
        refreshPinGraphics: app.refreshPinGraphics
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
            app.vue.master = tickets;
            app.vue.tickets = app.vue.master;
            app.vue.ticket_tags = result.data.ticket_tags.map((tag) => {
               tag.label = tag.tag_name;
               return tag;
            });
            return axios.get(get_pinned_tickets_url)
        }).then((result) => {
           app.data.pinned_tickets = result.data.pinned_tickets;
           app.refreshPinGraphics();
        }).then(() => {
            // handle if there's a tag input
            console.log(app.data.ticket_tags);
            if(tag_id != "None") {
                // find the tag for given ID
                foundTag = app.data.ticket_tags.find(tag => tag.id == tag_id);
                app.data.selected_tags.push(foundTag);
                app.filter_list();
            }
            if(assignee_id != "None") {
                foundAssignee = app.data.project_users.find(user => user.user == assignee_id);
                app.data.selected_users.push(foundAssignee);
                app.filter_list();
            }
        });
        axios.get(get_users_url).then((result) => {
            app.data.project_users = result.data.users.map((user) => {
                user.label = user.full_name;
                return user;
            }).filter((user) => { return user.role != "unapproved"});
        });

    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
