"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7346"],{40681:function(e,t,a){a.a(e,(async function(e,i){try{a.r(t),a.d(t,{HaFormInteger:function(){return _}});a(37216),a(32203),a(35748),a(62928),a(95013);var s=a(69868),h=a(84922),d=a(11991),l=a(73120),r=a(45810),o=(a(71978),a(20014),a(11934),e([r]));r=(o.then?(await o)():o)[0];let u,n,c,v,p,m=e=>e;class _ extends h.WF{focus(){this._input&&this._input.focus()}render(){var e,t;return void 0!==this.schema.valueMin&&void 0!==this.schema.valueMax&&this.schema.valueMax-this.schema.valueMin<256?(0,h.qy)(u||(u=m`
        <div>
          ${0}
          <div class="flex">
            ${0}
            <ha-slider
              labeled
              .value=${0}
              .min=${0}
              .max=${0}
              .disabled=${0}
              @change=${0}
            ></ha-slider>
          </div>
          ${0}
        </div>
      `),this.label,this.schema.required?"":(0,h.qy)(n||(n=m`
                  <ha-checkbox
                    @change=${0}
                    .checked=${0}
                    .disabled=${0}
                  ></ha-checkbox>
                `),this._handleCheckboxChange,void 0!==this.data,this.disabled),this._value,this.schema.valueMin,this.schema.valueMax,this.disabled||void 0===this.data&&!this.schema.required,this._valueChanged,this.helper?(0,h.qy)(c||(c=m`<ha-input-helper-text .disabled=${0}
                >${0}</ha-input-helper-text
              >`),this.disabled,this.helper):""):(0,h.qy)(v||(v=m`
      <ha-textfield
        type="number"
        inputMode="numeric"
        .label=${0}
        .helper=${0}
        helperPersistent
        .value=${0}
        .disabled=${0}
        .required=${0}
        .autoValidate=${0}
        .suffix=${0}
        .validationMessage=${0}
        @input=${0}
      ></ha-textfield>
    `),this.label,this.helper,void 0!==this.data?this.data:"",this.disabled,this.schema.required,this.schema.required,null===(e=this.schema.description)||void 0===e?void 0:e.suffix,this.schema.required?null===(t=this.localize)||void 0===t?void 0:t.call(this,"ui.common.error_required"):void 0,this._valueChanged)}updated(e){e.has("schema")&&this.toggleAttribute("own-margin",!("valueMin"in this.schema&&"valueMax"in this.schema||!this.schema.required))}get _value(){var e,t;return void 0!==this.data?this.data:this.schema.required?void 0!==(null===(e=this.schema.description)||void 0===e?void 0:e.suggested_value)&&null!==(null===(t=this.schema.description)||void 0===t?void 0:t.suggested_value)||this.schema.default||this.schema.valueMin||0:this.schema.valueMin||0}_handleCheckboxChange(e){let t;if(e.target.checked)for(const i of[this._lastValue,null===(a=this.schema.description)||void 0===a?void 0:a.suggested_value,this.schema.default,0]){var a;if(void 0!==i){t=i;break}}else this._lastValue=this.data;(0,l.r)(this,"value-changed",{value:t})}_valueChanged(e){const t=e.target,a=t.value;let i;if(""!==a&&(i=parseInt(String(a))),this.data!==i)(0,l.r)(this,"value-changed",{value:i});else{const e=void 0===i?"":String(i);t.value!==e&&(t.value=e)}}constructor(...e){super(...e),this.disabled=!1}}_.styles=(0,h.AH)(p||(p=m`
    :host([own-margin]) {
      margin-bottom: 5px;
    }
    .flex {
      display: flex;
    }
    ha-slider {
      flex: 1;
    }
    ha-textfield {
      display: block;
    }
  `)),(0,s.__decorate)([(0,d.MZ)({attribute:!1})],_.prototype,"localize",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:!1})],_.prototype,"schema",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:!1})],_.prototype,"data",void 0),(0,s.__decorate)([(0,d.MZ)()],_.prototype,"label",void 0),(0,s.__decorate)([(0,d.MZ)()],_.prototype,"helper",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,s.__decorate)([(0,d.P)("ha-textfield ha-slider")],_.prototype,"_input",void 0),_=(0,s.__decorate)([(0,d.EM)("ha-form-integer")],_),i()}catch(u){i(u)}}))}}]);
//# sourceMappingURL=7346.1e5594edb46b0424.js.map