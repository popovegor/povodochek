/* TYPEAHEAD
 * ========= */

!function($) {
  var defs = $.fn.typeahead.defaults,
      base = $.fn.typeahead.Constructor.prototype

  defs.items = 8
  defs.minLength = 2

  defs.source = function(query, process)
  {
    query = query.substr(0, this.options.minLength).toLowerCase()

    var that = this,
        items = this.queries[query]

    if (items) {
      return items
    }

    if (this.xhr) {
      this.xhr.abort()
    }

    this.xhr = $.ajax({
      url: this.options.url,
      data: { query: query },
      success: function(data)
      {
        that.queries[query] = items = []
        for(var i = 0; i < data.length; i++) {
          that.ids[data[i].val] = data[i].id
          items[i] = data[i].val
        }
        process(items)
      }
    })
  }

  base._updater = base.updater
  base._blur = base.blur
  base._listen = base.listen

  base.updater = function(item)
  {
    if (this.$id) {
      this.$id.val(this.ids[item])
    }
    return this._updater(item)
  }

  base.blur = function(e)
  {
    this.updater(this.$element.val())
    this._blur(e)
  }

  base.listen = function()
  {
    this.ids = {}
    this.queries = {}

    if (this.options.id) {
      this.$id = $('#' + this.options.id.replace(/(:|\.|\[|\])/g,'\\$1'))
      this.ids[this.$element.val()] = this.$id.val()
    }
    this._listen()
  }

}(jQuery)
