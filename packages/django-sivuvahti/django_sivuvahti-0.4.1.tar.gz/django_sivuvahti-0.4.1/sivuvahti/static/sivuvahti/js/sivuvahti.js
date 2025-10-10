"use strict";

(function () {
  function Sivuvahti (url, csrfmiddlewaretoken) {
    this.kantoaalto = new Kantoaalto(url, {
      kattelydata: JSON.stringify({csrfmiddlewaretoken}),
    });
    this.kantoaalto.then(function () {
      document.dispatchEvent(
        new Event("sivuvahti.yhteysAvattu")
      );
    }).then(this.vastaanota.bind(this));
    this.kantoaalto.katkaistu().then(function () {
      document.dispatchEvent(
        new Event("sivuvahti.yhteysKatkaistu")
      );
    });
  }

  Object.assign(Sivuvahti.prototype, {
    kasitteleSaapuvaSanoma: function (data) {
      if (data.saapuva_kayttaja)
        document.dispatchEvent(
          new CustomEvent(
            "sivuvahti.saapuvaKayttaja",
            {detail: data.saapuva_kayttaja}
          )
        );
      else if (data.poistuva_kayttaja)
        document.dispatchEvent(
          new CustomEvent(
            "sivuvahti.poistuvaKayttaja",
            {detail: data.poistuva_kayttaja}
          )
        );
      else if (data.saapuva_viesti)
        document.dispatchEvent(
          new CustomEvent(
            "sivuvahti.saapuvaViesti",
            {detail: data.saapuva_viesti}
          )
        );
    },

    vastaanota: function () {
      return new Promise(function (resolve, reject) {
        this.kantoaalto.vastaanota().then(function (data) {
          this.kasitteleSaapuvaSanoma(JSON.parse(data));
          return this.vastaanota();
        }.bind(this));
      }.bind(this));
    },

    laheta: function (viesti) {
      return this.kantoaalto.laheta(JSON.stringify(viesti));
    },

    sulje: function () {
      return this.kantoaalto.sulje();
    },

    avaa: function () {
      return this.kantoaalto.avaa();
    }
  });

  window.Sivuvahti = Sivuvahti;
})();
