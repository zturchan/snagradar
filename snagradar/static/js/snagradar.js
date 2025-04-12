var loadFile = function (event) {
  var output = document.getElementById('preview');
  output.src = URL.createObjectURL(event.target.files[0]);
  output.onload = function () {
    URL.revokeObjectURL(output.src) // free memory
  }
}

function display_ev_or_range(pokemon, stat){
  var range = pokemon['evs_range_' + stat];
  if (range[0] == range[1]){
    $("#evs_" + stat).text(range[0]);
  } else {
    $("#evs_" + stat).text(range[0] + '-' + range[1]);
  }
}

function evs_minimum_total(pokemon){
  var total = 0;
  stats = ['hp','atk','defense','spatk','spdef','speed']
  for(var i in stats){
    total += pokemon['evs_range_' + stats[i]][0];
  }
  return total;
}

$(document).ready(function () {
  
  $(document).on("click", ".clear-button", function(){
    $("form#form input, select").each(function(){
      $(this).val("");
    });
    $("#preview").attr("src", "");
  });

  $(document).on("click", "#nature-clear", function(){
    $("#nature").val('');
  });

  $("form#form").submit(function (e) {
    e.preventDefault();
    $('#snag-error').hide();
    $('#snag-info').hide();
    $('#snag-warning').hide();
    var formData = new FormData(this);
    $('.scan-spinner').addClass("active");

    // When using the FormData constructor, selects are not picked up so we need to add them
    $("form#form select").each(function(){
        var $select = $(this);
        formData.append($select.attr('name'), $select.val());
    });

    $.ajax({
      url: $(this).attr("action"),
      type: 'POST',
      data: formData,
      error: function(error){
        if (error.responseJSON){
          $('#error-text').text(error.responseJSON.description);
          $('#snag-error').show();
        } else {
          $('#error-text').text("An undefined server error occurred.");
          $('#snag-error').show();
        }
        $('.scan-spinner').removeClass("active");
      },
      success: function (pokemon) {
        $('.scan-spinner').removeClass("active");
        $("#hp-stat").val(pokemon['hp']);
        $("#atk-stat").val(pokemon['atk']);
        $("#defense-stat").val(pokemon['defense']);
        $("#spatk-stat").val(pokemon['spatk']);
        $("#spdef-stat").val(pokemon['spdef']);
        $("#speed-stat").val(pokemon['speed']);
        $("#evs_total").text(evs_minimum_total(pokemon));

        display_ev_or_range(pokemon, 'hp');
        display_ev_or_range(pokemon, 'atk');
        display_ev_or_range(pokemon, 'defense');
        display_ev_or_range(pokemon, 'spatk');
        display_ev_or_range(pokemon, 'spdef');
        display_ev_or_range(pokemon, 'speed');

        $("#pokemon-select").val(pokemon.name).change();
        $("#nature").val(pokemon.nature).change();
        $("#lvl").val(pokemon.lvl).change();
        if (pokemon.msg != null && pokemon.msg.length > 0){
          $('#warning-text').html(pokemon.msg);
          $('#snag-warning').show();
        } else {
          $('#snag-info').show();
          setTimeout(() => {
            $('#snag-info').hide();
          }, 5000);
        }
      },
      cache: false,
      contentType: false,
      processData: false
  });
  });
});
