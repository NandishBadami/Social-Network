document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.like').forEach(btn => {
        btn.onclick = () => {
            fetch(`/like/${btn.classList[3]}`)
            .then(response => response.json())
            .then(data => {   
                document.querySelectorAll('.likes').forEach(p => {
                    if(p.classList[1] == btn.classList[3]){
                        p.textContent = `Likes: ${data.likes}`;
                    }
                });
                if (btn.classList[1] == 'btn-primary') {
                    btn.textContent = 'UnLike';
                    btn.classList.replace('btn-primary', 'btn-danger')
                } else {
                    btn.textContent = 'Like'
                    btn.classList.replace('btn-danger', 'btn-primary')
                }
            });
        }
    });
    console.log("Hello")
});