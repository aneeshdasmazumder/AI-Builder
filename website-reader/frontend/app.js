$(function () {
  const $form = $("#reader-form");
  const $button = $("#submit-button");
  const $status = $("#status-pill");
  const $empty = $("#empty-state");
  const $result = $("#result");
  const $meta = $("#meta");

  function setLoading(isLoading) {
    $button.prop("disabled", isLoading).toggleClass("is-loading", isLoading);
    $status.removeClass("error").text(isLoading ? "Working" : "Ready");
  }

  function showResult(text, metaText) {
    $empty.attr("hidden", true);
    $result.removeClass("error").text(text).removeAttr("hidden");
    $meta.text(metaText || "").prop("hidden", !metaText);
    $status.removeClass("error").text("Done");
  }

  function showError(message) {
    $empty.attr("hidden", true);
    $result.addClass("error").text(message).removeAttr("hidden");
    $meta.prop("hidden", true);
    $status.addClass("error").text("Error");
  }

  $form.on("submit", function (event) {
    event.preventDefault();

    const payload = {
      url: $("#website-url").val().trim(),
      prompt: $("#user-prompt").val().trim()
    };

    if (!payload.url || !payload.prompt) {
      showError("Please enter both a website URL and a prompt.");
      return;
    }

    setLoading(true);
    $result.removeAttr("hidden").removeClass("error").text("Fetching and analyzing the website...");
    $empty.attr("hidden", true);
    $meta.prop("hidden", true);

    $.ajax({
      url: "/api/summarize",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
      dataType: "json"
    })
      .done(function (data) {
        if (!data.ok) {
          showError(data.error || "Something went wrong.");
          return;
        }

        const metaText = `Read ${data.usedCharacters.toLocaleString()} of ${data.sourceCharacters.toLocaleString()} extracted characters.`;
        showResult(data.summary, metaText);
      })
      .fail(function (xhr) {
        const response = xhr.responseJSON;
        showError((response && response.error) || "The request failed. Check the server terminal for details.");
      })
      .always(function () {
        setLoading(false);
      });
  });
});
