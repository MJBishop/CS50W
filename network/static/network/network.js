document.addEventListener('DOMContentLoaded', function() {

    console.log('DOM ready')

    document.querySelector('#new-post-button').addEventListener('click', function(event) {
        console.log('new-post-button click')

        let toggleId = event.target.dataset.toggleId;
        if (toggleId) {
            let elem = document.getElementById(toggleId);
            elem.hidden = !elem.hidden;
        }
    });

    document.querySelector('#save-post-button').addEventListener('click', function(event) {
        console.log('save-post-button click')
        save_post()
    });

    document.querySelectorAll('#update-post-button').forEach(function(button) {
        button.onclick = function() {
            console.log('update-post-button click')
            update_post(button.dataset.post_id)
        }
    });

    document.querySelectorAll('#like-post-button').forEach(function(button) {
        button.onclick = function() {
            console.log('like-post-button click')
            like_post()
        }
    });

    document.querySelector('#follow-user-button').addEventListener('click', function(event) {
        console.log('follow-user-button click')
        toggle_follow()
    });
    
});

  
function save_post() {
    console.log('save_post')
    
    // Save the new Post
    const path = '/post';
    fetch(path, {
        method: 'POST',
        body: JSON.stringify({
            text: document.querySelector('#new-post-text').value
        })
    })
    // catch json response!!?

    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });

    // Prevent default submission
    return false;
}

function update_post(post_id) {
    console.log('update_post')
    console.log(post_id)

    if (post_id) {
        let elem = document.getElementById(post_id);
        var post_text = elem.querySelector("#post_text");
        var text = post_text.innerText

        // swap in text area
        const text_area = document.createElement('textarea');
        text_area.classList.add('form-control');
        text_area.setAttribute('id', 'update-post-text');
        // populate with text
        text_area.value = text;
        post_text.innerHTML = '';
        post_text.append(text_area);

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
        const div = document.createElement('div')
        div.setAttribute('id', 'save-updated-post-div');
        div.append(save_updated_post_button);
        elem.append(div);

    }
}

function save_updated_post(post_id) {
    console.log('save_updated_post')

    // swap in submit button
    console.log(post_id)

    var new_text = document.querySelector('#update-post-text').value

    if (post_id) {
        let elem = document.getElementById(post_id);
        var post_text = elem.querySelector("#post_text");
        post_text.innerText = new_text

        // hide update-post-button
        var post_buttons = elem.querySelector("#post-buttons");
        post_buttons.hidden = false;

        // append save button inside div
        const div = document.getElementById('save-updated-post-div');
        div.remove();

    }

    // Save the new Post
    const path = '/post/' + post_id;
    fetch(path, {
        method: 'PUT',
        body: JSON.stringify({
            text: new_text
        })
    })
    // catch json response!!?

    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });

    // Prevent default submission
    return false;
}

function like_post() {
    console.log('like_post')

    // toggle like

}

function toggle_follow() {
    console.log('toggle_follow')

    // follow 


    // unfollow

}
  
