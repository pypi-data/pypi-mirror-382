if (parent.callback) {
    //如果是在子框架内就把首页刷新
    parent.callback();
}
var loginApp = new Vue({
    el: '#vue_app',
    data: {
        username: '',
        password: '',
        loading: false
    },
    methods: {
        login() {
            this.loading = true;
            if (this.username === "" || this.password === "") {
                this.$message.error("Please enter your username or password!");
                this.loading = false;
                return ;
            }
            this.$nextTick(function () {
                document.getElementById('login-form').submit();
            });
        },
        third(t){
          fetch(`/echart/third_login/?t=${t}`)
            .then(async (response) => {
            const data = await response.json();
            if (data.status === 200) {
            window.location.href = data.msg;
             } else {this.$message.error(data.msg);}
           });
        },
    }
});