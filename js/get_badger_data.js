function getPopupData(tabId) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({
      type: "getPopupData",
      tabId: tabId,
    }, function(res) {
      resolve(res)
    })
  })
}

function getOpenTabs() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({}, function (res) {
      resolve(res)
    })
  })
}

let tabs = await getOpenTabs()
if (tabs.length > 0) {
    let tabId = tabs[0].id
    let popup = await getPopupData(tabId)
    return popup
} else {
    return false
}