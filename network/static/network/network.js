document.addEventListener('DOMContentLoaded', function() {

    console.log('DOM ready')

    // Update Post
    enable_all_edit_buttons();

    // Like Post
    document.querySelectorAll('#like-post-button').forEach(function(button) {
        button.onclick = function() {
            // console.log('like-post-button click') 
            like_post(button)
        }
        // if post in user.liked_posts
    });

    // Follow User
    var follow_user_button = document.querySelector('#follow-user-button');
    if (follow_user_button) {
        follow_user_button.addEventListener('click', function(event) {
            // console.log('follow-user-button click') 
            toggle_follow(follow_user_button)
        });
    }
    
});

function editing_edit_buttons(post_id) {
    document.querySelectorAll('#update-post-button').forEach(function(button) {
        button.onclick = function() {
            // console.log('update-post-button click')
            end_editing_post(post_id, null);
            update_post(button.dataset.post_id)
        }
    });
}

function enable_all_edit_buttons() {
    document.querySelectorAll('#update-post-button').forEach(function(button) {
        button.onclick = function() {
            // console.log('update-post-button click')
            update_post(button.dataset.post_id)
        }
    });
}


function update_post(post_id) {
    // console.log('update_post')
    // console.log(post_id)

    if (post_id) {
        let elem = document.getElementById(post_id);

        // 
        var post_text = elem.querySelector("#post-text");
        var text = post_text.innerText
        post_text.hidden = true;

        // create text area
        const text_area = document.createElement('textarea');
        text_area.classList.add('form-control');
        text_area.setAttribute('id', 'update-post-text');
        // populate with text
        text_area.value = text;
        // append to post-text-div
        var post_text_div = elem.querySelector("#post-text-div");
        post_text_div.append(text_area);

        // hide update-post-button
        var post_buttons = elem.querySelector("#post-buttons");
        post_buttons.hidden = true;

        // create new save button
        const save_updated_post_button = document.createElement('button');
        save_updated_post_button.classList.add('btn', 'btn-sm', 'btn-primary', 'mt-2');
        save_updated_post_button.setAttribute('id', 'save-updated-post-button');
        save_updated_post_button.setAttribute('data-post_id', post_id);
        save_updated_post_button.textContent = 'Save'
        save_updated_post_button.addEventListener('click', function(button) {
            save_updated_post(post_id)
        });

        // append save button inside div
        const button_col_div = document.createElement('div')
        button_col_div.classList.add('col-12');
        button_col_div.append(save_updated_post_button);

        const button_row_div = document.createElement('div')
        button_row_div.classList.add('row');
        button_row_div.setAttribute('id', 'save-updated-post-div');
        button_row_div.append(button_col_div);
        elem.append(button_row_div);

        // disable editing buttons
        editing_edit_buttons(post_id);

    }
}

function save_updated_post(post_id) {
    
    // todo - check for changes to post text

    
    var new_text = document.querySelector('#update-post-text').value

    // Save the new Post
    const path = '/post/' + post_id;
    fetch(path, {
        method: 'PUT',
        body: JSON.stringify({
            text: new_text
        })
    })
    .then(response => response.json())
    .then(data => {
        // Log data to the console
        console.log(data);

        if (data.error) {
            
            // end editing post - original text
            end_editing_post(post_id, null)

            // Present general error alert - todo!

        } 
        else if (data.validation_error) {

            // Present warning alert - todo!

        }
        else if (data.message) {

            // end editing post - new_text
            end_editing_post(post_id, new_text);

            // Present success alert - todo!
        }
    })

    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });

    // Prevent default submission
    return false;
}

function end_editing_post(post_id, new_text) {

    // unhide Post text
    let elem = document.getElementById(post_id);
    var post_text = elem.querySelector("#post-text");
    post_text.hidden = false;

    // Update Post text
    if (new_text) {
        post_text.innerText = new_text
    }

    // remove textarea
    var textarea = elem.querySelector("#update-post-text");
    textarea.remove();

    // show post-buttons
    var post_buttons = elem.querySelector("#post-buttons");
    post_buttons.hidden = false;

    // remove save button div
    const div = document.getElementById('save-updated-post-div');
    div.remove();


    // enable all editing buttons
    enable_all_edit_buttons();
}

function like_post(button) {
    console.log('like_post')

    post_id = button.dataset.post_id;

    // toggle like
    const path = '/like/' + post_id;
    fetch(path, {
        method: 'PUT',
    })
    .then(response => response.json())
    .then(data => {
        // Log data to the console
        console.log(data);

        if (data.error) {
            
            // 

            // Present general error alert - todo!

        } 
        else if (data.message) {

            // update
            button.innerHTML = "Likes " + data.likes;

            // todo: update ui: like or not like
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-primary');

            // Present success alert - todo!
        }
    })

    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });

    // Prevent default submission
    return false;

}

function toggle_follow(button) {
    console.log('toggle_follow')
    console.log(button.dataset.profile_id)

    var profile_id = button.dataset.profile_id;
    const followers_count_div = document.getElementById('followers-count-div');

    if (button.dataset.following === "following") {
        // unfollow

        const path = '/unfollow/' + profile_id;
        fetch(path, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            // Log data to the console
            console.log(data);

            if (data.error) {
                
                // 

                // Present general error alert - todo!

            } 
            else if (data.message) {

                // update button
                button.dataset.following = "";
                button.innerText = "Follow";
                button.classList.add('btn-outline-primary');
                button.classList.remove('btn-primary');

                // update count
                followers_count_div.innerText = "followers " + data.followers

                // Present success alert - todo!
            }
        })

        // Catch any errors and log them to the console
        .catch(error => {
            console.log('Error:', error);
        });

        // Prevent default submission
        return false;
    }
    else {
        // follow 

        const path = '/follow/' + profile_id;
        fetch(path, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            // Log data to the console
            console.log(data);

            if (data.error) {
                
                // 

                // Present general error alert - todo!

            } 
            else if (data.message) {

                // update button
                button.dataset.following = "following";
                button.innerText = "Following";
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-primary');

                // update count
                followers_count_div.innerText = "followers " + data.followers

                // Present success alert - todo!
            }
        })

        // Catch any errors and log them to the console
        .catch(error => {
            console.log('Error:', error);
        });

        // Prevent default submission
        return false;
    }
}
  
