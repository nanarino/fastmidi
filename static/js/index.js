window.onload = () => {
  document.getElementById('form').onsubmit = async function (e) {
    e.preventDefault()
    const data = new FormData(this)
    data.set("li", data.get('li').split('\n').reduce((li, s) => li + s, '0'))
    const res = await fetch('/midi', { method: "POST", body: data })
    const a = document.createElement('a'), url = window.URL.createObjectURL(await res.blob())
    a.href = url
    a.download = res.headers.get('content-disposition').split('filename=')[1]
    a.click()
    window.URL.revokeObjectURL(url)
  }
}