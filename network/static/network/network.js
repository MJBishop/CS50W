document.addEventListener('DOMContentLoaded', function() {

    console.log('DOM ready')

    // document.querySelector('#post-list-view').addEventListener('click', function(event) {
    //     console.log('button click')
    
    // });
    
});

// can i add to specific element? yes?
document.addEventListener('click', function(event) {
    console.log('click')

    let toggleId = event.target.dataset.toggleId;
    if (toggleId) {
        let elem = document.getElementById(toggleId);
        elem.hidden = !elem.hidden;
    }
    else {
        let id = event.target.id;
        if (id === 'save-post-button') {

            console.log('saving_post')
            save_post()
        }
        else if (id === 'update-post-button') {

            console.log('updating_post')
            update_post()
        }
        else if (id === 'like-post-button') {

            console.log('liking_post')
            like_post()
        }
        else if (id === 'follow-post-button') {

            console.log('toggle_following_post')
            toggle_follow()
        }
        else {
            console.log('click with no action')
            // better way to implement this??
        }
    }
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

function update_post() {
    console.log('update_post')

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
  
