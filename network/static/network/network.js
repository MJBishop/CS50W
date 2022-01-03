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
        
    }
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
  
