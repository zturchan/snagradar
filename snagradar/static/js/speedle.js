function pacific_time(date) {
    return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {timeZone: 'America/Vancouver'}));   
}

function now_pt(){
    return pacific_time(new Date());
}

function today_pt(){
    return now_pt().toDateString();
}

function result_text(result){
    switch(Number(result)){
        case -1: 
            return "Always outspeeds";
        case 0: 
            return "Sometimes outspeeds";
        case 1: 
            return "Sometimes outspeeds";
        default:
            return "Something went wrong!";
    }
}

function get_time_until_next_midnight_pacific(){
    var current_time_pt = now_pt();
    var h = current_time_pt.getHours();
    var m = current_time_pt.getMinutes();
    var s = current_time_pt.getSeconds();
    var secondsUntilEndOfDate = (24*60*60) - (h*60*60) - (m*60) - s;

    return new Date(1000 * secondsUntilEndOfDate).toISOString().substr(11, 8);
}

async function toast(text, is_correct){
    let background = is_correct ? 
    "linear-gradient(to left, rgb(0, 255, 0), #185f22)"
    : "linear-gradient(to left, rgb(255, 0, 0), #720101)";

    // Display the toast longer for incorrect answers so the user can read the correct one
    let duration = is_correct ? 1000 : 2000;
    await Toastify({
  text: text,
  duration: duration,
  gravity: "top", 
  position: "center",
  stopOnFocus: true, 
  style: {
    background: background,
  },
    offset: {
    y: 220 // vertical axis - can be a number or a string indicating unity. eg: '2em'
  },
  onClick: function(){} // Callback after click
}).showToast();
await new Promise(r => setTimeout(r, duration));

}

async function setClipboard(text) {
  const type = "text/plain";
  const clipboardItemData = {
    [type]: text
  };
  const clipboardItem = new ClipboardItem(clipboardItemData);
  await navigator.clipboard.write([clipboardItem]);
}



window.onload = (event) => {
    

    let matches = document.querySelectorAll(".challenge-container");

    matches[0].style.display = "block";
    let current_index = 0;
    let user_score = [];

    document.addEventListener("click", (e) => {
    const button = e.target.closest(".share");
    if (button) {
        let emoji_results = user_score.map(x => x === true ? "🔴" : "⚫");
        setClipboard("Pokemon Speedle for " + today_pt() + "\r\n" + emoji_results.join("") + "\r\n" + window.location);
        button.textContent = "Copied!";
    }
    });

    document.querySelectorAll("table.buttons button").forEach(function(button){
                button.addEventListener('click', async function() {
                        let user_answer = this.dataset.value;
                        let correct_answer = this.closest(".challenge-container").dataset.result
                        var ball_icon =  document.getElementsByClassName("ball " + current_index)[0];
                        if (user_answer == correct_answer){
                            user_score.push(true);
                            await toast("Correct!", true)
                        } else{
                            user_score.push(false);
                            ball_icon.classList.add("wrong");
                            await toast("Incorrect! " + result_text(correct_answer), false)
                        }

                        ball_icon.classList.remove("default");

                        matches[current_index].style.display = "none";
                        ++current_index;

                        if (current_index < matches.length){
                            matches[current_index].style.display = "block";
                        }

                        if (current_index == 10){
                            const correct_answers = user_score.filter(x => x === true).length;


                            summary = document.getElementById("daily-summary");

                            let score = document.createElement("p");
                            score.append(correct_answers + "/10");
                            let share = document.createElement("button");
                            share.classList.add("share");
                            share.classList.add("btn");
                            share.classList.add("btn-success");
                            share.append("Share")
                            score.append(share);
                            summary.append(score);
                            

                            let result = document.createElement("p");

                            if (correct_answers == 10){
                                result.append("Awesome, you're a pokemon master!");
                            }
                            else if (correct_answers > 7){
                                result.append("Great Job, keep up the good work!");
                            }
                            else if (correct_answers > 4){
                                result.append("You're getting there, keep training!");
                            }
                            else {
                                result.append("You're light-years away from beating Brock.");
                            }
                            
                            summary.append(result);
                            
                            let play_tomorrow = document.createElement("p");
                            play_tomorrow.append("You can play tomorrow's challenge in:");
                            play_tomorrow.append(get_time_until_next_midnight_pacific());
                            summary.append(play_tomorrow);
                            

                            summary.style.display = "block";
                        }
         }, false);

    }    );
};