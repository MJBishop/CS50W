document.addEventListener('DOMContentLoaded', function() {

    console.log('DOM ready')

    var new_post_button = document.querySelector('#new-post-button')
    if (new_post_button) {
        new_post_button.addEventListener('click', function(event) {
            // console.log('new-post-button click')
    
            let toggleId = event.target.dataset.toggleId;
            if (toggleId) {
                let elem = document.getElementById(toggleId);
                elem.hidden = !elem.hidden;
            }
        });
    }
    
    var save_post_button = document.querySelector('#save-post-button')
    if (save_post_button) {
        save_post_button.addEventListener('click', function(event) {
            // console.log('save-post-button click')
            save_new_post()
        });
    }
    

    document.querySelectorAll('#update-post-button').forEach(function(button) {
        button.onclick = function() {
            // console.log('update-post-button click')
            update_post(button.dataset.post_id)
        }
    });

    document.querySelectorAll('#like-post-button').forEach(function(button) {
        button.onclick = function() {
            console.log('like-post-button click')
            like_post(button)
        }
    });

    var follow_user_button = document.querySelector('#follow-user-button');
    if (follow_user_button) {
        follow_user_button.addEventListener('click', function(event) {
            console.log('follow-user-button click')
            toggle_follow(follow_user_button)
        });
    }
    
});

  
function save_new_post() {
    // console.log('save_post')
    
    // Save the new Post
    const path = '/post';
    fetch(path, {
        method: 'POST',
        body: JSON.stringify({
            text: document.querySelector('#new-post-text').value
        })
    })
    .then(response => response.json())
    .then(data => {
        // Log data to the console
        console.log(data);
        
        if (data.error) {

            // Present general error alert - todo!

        } 
        else if (data.validation_error) {
            // todo:
            // !! stop removal of form !! - toggle?

            // Present warning alert - todo!

        }
        else if (data.message) {
            console.log("No errors")

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

function update_post(post_id) {
    // console.log('update_post')
    // console.log(post_id)

    // todo:
    // disable other buttons
    // disallow multiple edits

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
        save_updated_post_button.classList.add('btn', 'btn-sm', 'btn-outline-primary', 'mt-2');
        save_updated_post_button.setAttribute('id', 'save-updated-post-button');
        save_updated_post_button.setAttribute('data-post_id', post_id);
        save_updated_post_button.textContent = 'Save'
        save_updated_post_button.addEventListener('click', function(button) {
            save_updated_post(post_id)
        });

        // append save button inside div
        const button_div = document.createElement('div')
        button_div.setAttribute('id', 'save-updated-post-div');
        button_div.append(save_updated_post_button);
        elem.append(button_div);

    }
}

function save_updated_post(post_id) {
    
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

    // follow 


    // unfollow

}
  
