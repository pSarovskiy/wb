const instance = axios.create({
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: "X-CSRFTOKEN",
});

const store = Vuex.createStore({
    state () {
        return {
            items: [],
            items_down: [],
            items_up: []
        }
    },
    getters: {
        ITEMS(state) { return state.items },
        ITEMS_COUNT(state) { return state.items.length; },
        ITEMS_UP(state) { return _.orderBy(state.items_up, ['views'], 'desc') },
        ITEMS_UP_COUNT(state) { return state.items_up.length; },
        ITEMS_DOWN(state) { return _.orderBy(state.items_down, ['views'], 'desc') },
        ITEMS_DOWN_COUNT(state) { return state.items_down.length; },
        ITEMS_ALL_COUNT(state, getters) { return getters.ITEMS_COUNT + getters.ITEMS_UP_COUNT + getters.ITEMS_DOWN_COUNT; },
        ITEMS_NEW_COUNT(state, getters) {
            let newCount = 0
            getters.ITEMS_DOWN.forEach(function (item){ if (item.views) newCount ++; })
            return newCount;
        }
    },
    mutations: {
        SET_PRODUCTS_TO_STATE: (state, items) => {
            state.items = items.items;
            state.items_down = items.items_down;
            state.items_up = items.items_up;
        },
    },
    actions: {
        GET_PRODUCTS_FROM_API({commit}){
            return axios.get('/api/list')
                .then((response) => {
                    commit('SET_PRODUCTS_TO_STATE', response.data.items);
                    return response.data.items;
                })
                .catch((error) => {
                    console.log(error);
                    return error;
                })
        }
    }
});

const List = {
    data() {
        return {
            addItems: '',
            addItemsLoading: false,
            messages: '',
            url: '',
            newCountItem: 0
        };
    },
    watch: {
        url: function (newUrl){
            this.addItemsLoading = true;
            this.messages = '';
            const urlArray = this.$store.state.items.map(function(el) { return el.fields.url; });

            if ( urlArray.indexOf(newUrl) !== -1 ){
                this.messages = 'Этот товар уже отслеживается...'
                this.addItemsLoading = false;
            }else if (newUrl !== '') {
                this.loadItem(newUrl);
            }else{
                this.addItemsLoading = false;
            }
        }
    },
    mounted() {
        store.dispatch('GET_PRODUCTS_FROM_API');
        document.title = 'Отслеживаются' + ' ' + this.$store.getters.ITEMS_ALL_COUNT + ' това' + this.getNumEnding(this.$store.getters.ITEMS_ALL_COUNT, ['р','ра','ров']) + this.newItems(this.$store.getters.ITEMS_NEW_COUNT);
        this.update_store();
    },
    methods: {
        newItems(count){
            this.newCountItem = count
            return count > 0 ? ', ' + count + ' новы' + this.getNumEnding(count, ['й','х','х']) : '';
        },
        update_store() {
            setInterval(() => { store.dispatch('GET_PRODUCTS_FROM_API')}, 5 * 60 * 1000 )
        },
        loadItem: function (link) {
            axios({
                method : "POST",
                url: '/api/data/',
                data : { link: link },
            }).then(response => {
                this.addItems = response.data.item
                this.addItemsLoading = false;
                this.url = '';
            })
        },
        price_round(nums){
            return parseFloat(nums)
        },
        pricesClass(prices, index){
            let price = prices[index].price
            let oldPrice = index === 0 ? prices[index].price : prices[index - 1].price
            return oldPrice < price ? 'red' : ( oldPrice > price ? 'green' : '' );
        },
        itemPrice(item){
            let setPrice = this.price_round(item.fields.price);
            let startPrice = this.price_round(item.fields.start_price);
            let newPrice = this.price_round(item.fields.price);
            let oldPrice = this.price_round(item.fields.old_price);
            if (oldPrice < newPrice) {
                let diffPrice = newPrice - oldPrice;
                setPrice = '<span class="red">' + newPrice + '&nbsp;₽</span><span class="grey">стоил ' + oldPrice + ' p.</span><span class="grey">+ ' + diffPrice + ' p.</span>'
            } else if (oldPrice > newPrice) {
                let diffPrice = oldPrice - newPrice;
                setPrice = '<span class="green">' + newPrice + '&nbsp;₽</span><span class="grey">стоил ' + oldPrice + ' p.</span><span class="grey">дешевле на ' + diffPrice + ' p.</span>'
            } else {
                setPrice = newPrice + '&nbsp;₽';
            }
            if (newPrice === startPrice) setPrice = newPrice + '&nbsp;₽';
            if (newPrice === 0) setPrice = '<span class="grey">Нет в наличии</span>';
            document.title = 'Подешеве'+ this.getNumEnding(this.$store.getters.ITEMS_DOWN_COUNT, ['л','ли','ли']) + ' ' + this.$store.getters.ITEMS_DOWN_COUNT + ' ' + this.getNumEnding(this.$store.getters.ITEMS_DOWN_COUNT, ['товар','товара','товаров']) + this.newItems(this.$store.getters.ITEMS_NEW_COUNT);
            return setPrice;
        },
        add: function (link) {
            axios({
                method : "POST",
                url: '/api/add/',
                data : {
                    url: link,
                    title: this.addItems.title,
                    image: this.addItems.image,
                    price: this.addItems.price,
                    descr: this.addItems.descr,
                },
            }).then(response => {
                this.addItems = '';
                store.dispatch('GET_PRODUCTS_FROM_API')
            });
        },
        del: function (id) {
            axios.get('/api/delete/' + id + '/')
            .then(() => {
                store.dispatch('GET_PRODUCTS_FROM_API')
            })
        },
        views(id, views) {
            if (views){
                axios.get('/api/views/' + id + '/')
                .then(() => {
                    document.title = 'Подешеве'+ this.getNumEnding(this.$store.getters.ITEMS_DOWN_COUNT, ['л','ли','ли']) + ' ' + this.$store.getters.ITEMS_DOWN_COUNT + ' ' + this.getNumEnding(this.$store.getters.ITEMS_DOWN_COUNT, ['товар','товара','товаров']) + this.newItems(this.newCountItem > 0 ? this.newCountItem - 1 : 0);
                    document.getElementById('bages-'+ id).style.display = 'none';
                })
            }
        },
        pricesChart(prices){
            let chartArr = [];
            let priceStart = parseInt(prices[0].price);
            const priceMax = Math.max.apply(null, prices.map(p => { return parseInt(p.price) } ))
            prices.map(p => {
                const price = parseInt(p.price)
                const color = price < priceStart ? 'green' : (price > priceStart ? 'red' : '')
                const priceDiff = (price - priceStart) <= 0 ? (price - priceStart) : '+' + (price - priceStart)
                const priceDate = new Date(p.pub_date)
                let mon = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
                const title = priceDate.getDate() +' '+ mon[priceDate.getMonth()] + ' ' + price + '&nbsp;₽ ('+ priceDiff +')'
                chartArr.push('<div title="' + title + '" class="chart-item '+ color +'" style="height: ' + Math.round(price * 100 / priceMax) + '%"></div>');

                priceStart = price
            })
            return chartArr.join('')
        },
        getNumEnding: function (iNumber, aEndings){
            let sEnding, i;
            iNumber = iNumber % 100;
            if (iNumber>=11 && iNumber<=19) {
                sEnding=aEndings[2];
            }
            else {
                i = iNumber % 10;
                switch (i)
                {
                    case (1): sEnding = aEndings[0]; break;
                    case (2):
                    case (3):
                    case (4): sEnding = aEndings[1]; break;
                    default: sEnding = aEndings[2];
                }
            }
            return sEnding;
        }
    },
    template: `
        <div class="forms mt-3 mb-5">
            <div class="forms--input py-3 px-4 mb-3 d-flex align-items-center">
                <input id="addItemsInput" type="text" name="url" v-model="url" placeholder="Для отслеживания введи ссылку на товар" autocomplete="off">
                <div v-show="addItemsLoading" class="spinner-grow spinner-grow-sm ms-2" role="status"><span class="visually-hidden">Загрузка...</span></div>
            </div>
            <div class="messages mb-3" v-if="messages">{{ messages }}</div>
            <transition name="fade">
                <div class="items" v-if="addItems">
                    <div class="items--item d-flex p-4 mb-3 align-items-center">
                        <div class="items--item--image me-4" :style="{ backgroundImage: 'url(' + addItems.image + ')' }"></div>
                        <div class="items--item--title"><h3 class="mb-0">{{ addItems.title }}</h3></div>
                        <div class="items--item--content ms-auto d-flex align-items-center">
                            <div class="items--item--price ms-5">{{ addItems.price }}</div>
                            <div class="items--item--button ms-4">
                                <button class="button bg-red" type="submit" @click="add(addItems.url)">Следить</button>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
        <div class="items mb-5" v-if="this.$store.getters.ITEMS_DOWN_COUNT > 0">
            <h2 class="title mb-3">
                Подешеве{{ getNumEnding(this.$store.getters.ITEMS_DOWN_COUNT, ['л','ли','ли']) }} {{this.$store.getters.ITEMS_DOWN_COUNT}} {{ getNumEnding(this.$store.getters.ITEMS_DOWN_COUNT, ['товар','товара','товаров']) }}
            </h2>
            <transition-group name="list-complete" tag="section">
                <div @mouseover="views(item.pk, item.views)" class="items--item d-flex p-4 mb-3 align-items-center" v-for="(item, index) in this.$store.getters.ITEMS_DOWN" :key="item.pk">
                    <div :id="'bages-'+ item.pk" :class="[{'hide': !item.views}, 'bages']" v-if="item.views">Новый</div>
                    <div class="items--item--image me-4 flex-shrink-0 mb-auto" :style="{ backgroundImage: 'url(media/' + item.fields.image + ')' }"></div>
                    <div class="items--item--title position-relative">
                        <h3 class="mb-0">{{ item.fields.title }}</h3>
                        <div v-if="item.prices && item.prices.length > 1" class="items--item--prices d-flex flex-wrap mt-2">
                            <div class="items--item--prices--chart d-flex align-items-end" v-html="pricesChart(item.prices)"></div>
                        </div>
                    </div>
                    <div class="items--item--content ms-auto d-flex align-items-center">
                        <div class="items--item--price ms-5 d-flex flex-column align-items-end" v-html="itemPrice(item)"></div>
                        <div class="items--item--button ms-4 text-center">
                            <a class="button" :href="item.fields.url" target="_blank" rel="noreferrer">В магазин</a>
                            <div class="button small bg-red mt-1" @click="del(item.pk)" title="Прекратить отслеживать товар">Удалить</div>
                        </div>
                    </div>
                </div>
            </transition-group>
        </div>
        <div class="items mb-5" v-if="this.$store.getters.ITEMS_UP_COUNT > 0">
            <h2 class="title mb-3">
                Подорожа{{ getNumEnding(this.$store.getters.ITEMS_UP_COUNT, ['л','ли','ли']) }} {{this.$store.getters.ITEMS_UP_COUNT}} {{ getNumEnding(this.$store.getters.ITEMS_UP_COUNT, ['товар','товара','товаров']) }}
            </h2>
            <transition-group name="list-complete" tag="section">
                <div @mouseover="views(item.pk, item.views)" class="items--item d-flex p-4 mb-3 align-items-center" v-for="(item, index) in this.$store.getters.ITEMS_UP" :key="item.pk">
                    <div :id="'bages-'+ item.pk" :class="[{'hide': !item.views}, 'bages']" v-if="item.views">Новый</div>
                    <div class="items--item--image me-4 flex-shrink-0 mb-auto" :style="{ backgroundImage: 'url(media/' + item.fields.image + ')' }"></div>
                    <div class="items--item--title position-relative">
                        <h3 class="mb-0">{{ item.fields.title }}</h3>
                        <div v-if="item.prices && item.prices.length > 1" class="items--item--prices d-flex flex-wrap mt-2">
                            <div class="items--item--prices--chart d-flex align-items-end" v-html="pricesChart(item.prices)"></div>
                        </div>
                    </div>
                    <div class="items--item--content ms-auto d-flex align-items-center">
                        <div class="items--item--price ms-5 d-flex flex-column align-items-end" v-html="itemPrice(item)"></div>
                        <div class="items--item--button ms-4 text-center">
                            <a class="button" :href="item.fields.url" target="_blank" rel="noreferrer">В магазин</a>
                            <div class="button small bg-red mt-1" @click="del(item.pk)" title="Прекратить отслеживать товар">Удалить</div>
                        </div>
                    </div>
                </div>
            </transition-group>
        </div>
        <div class="items" v-if="this.$store.getters.ITEMS_COUNT > 0">
            <h2 class="title mb-3">
                У {{this.$store.getters.ITEMS_COUNT}} {{ getNumEnding(this.$store.getters.ITEMS_COUNT, ['товара','товаров','товаров']) }} цена не изменилась
            </h2>
            <transition-group name="list-complete" tag="section">
                <div class="items--item d-flex p-4 mb-3 align-items-center" v-for="(item, index) in this.$store.getters.ITEMS" :key="item.pk">
                    <div class="items--item--image me-4 flex-shrink-0 mb-auto" :style="{ backgroundImage: 'url(media/' + item.fields.image + ')' }"></div>
                    <div class="items--item--title position-relative">
                        <h3 class="mb-0">{{ item.fields.title }}</h3>
                        <div v-if="item.prices && item.prices.length > 1" class="items--item--prices d-flex flex-wrap mt-2">
                            <div class="items--item--prices--chart d-flex align-items-end" v-html="pricesChart(item.prices)"></div>
                        </div>
                    </div>
                    <div class="items--item--content ms-auto d-flex align-items-center">
                        <div class="items--item--price ms-5 d-flex flex-column align-items-end" v-html="itemPrice(item)"></div>
                        <div class="items--item--button ms-4 text-center">
                            <a class="button" :href="item.fields.url" target="_blank" rel="noreferrer">В магазин</a>
                            <div class="button small bg-red mt-1" @click="del(item.pk)" title="Прекратить отслеживать товар">Удалить</div>
                        </div>
                    </div>
                </div>
            </transition-group>
        </div>
    `
}

const routes = [
  { path: '/', component: List },
]

const router = VueRouter.createRouter({
  history: VueRouter.createWebHashHistory(),
  routes,
})

const app = Vue.createApp({})
app.use(router)
app.use(store)
app.mount('#app')

