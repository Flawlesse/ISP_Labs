import React from 'react';
import './App.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { fab } from '@fortawesome/free-brands-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { BrowserRouter, Route, Redirect } from 'react-router-dom'
import { axiosInstance } from '../database/axios'
import LoginForm from './auth/LoginForm'
import RegisterForm from './auth/RegisterForm'
import OrderList from './order/OrderList'
import OrderItem from './order/OrderItem'
import OrderForm from './order/OrderForm'

library.add(fab, fas)

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loggedIn: false,
    }
  }
  componentDidMount() {
    this.checkLoggedIn()
  }

  checkLoggedIn = () => {
    let token = window.localStorage.getItem('access_token')
    if (token === null) {
      this.setState(({
        loggedIn: false,
      }))
    }
    else {
      axiosInstance.get('profile/')
        .then((response) => {
          if (response.status === 200) {
            this.setState(({
              loggedIn: true,
            }))
          }
        })
        .catch((errors) => {
          if (errors.response.status === 401) {
            console.log(errors.response);
            this.setState(({
              loggedIn: false,
            }))
          }
          else {
            console.log(`STATUS: ${errors.response.status}`)
            console.log(errors.response);
          }
          console.log("I'm about to remove access token...");
          window.localStorage.removeItem('access_token')
          window.dispatchEvent(new StorageEvent('storage', {
            storageArea: window.localStorage,
            key: "access_token",
            newValue: null,
          }))
        })
    }
  }

  render() {
    return (
      <BrowserRouter>
        <Route path="/accounts/login" component={LoginForm} />
        <Route path="/accounts/register" component={RegisterForm} />

        <Route exact path="/"><Redirect to="/orders" /></Route>
        <Route exact path="/orders" component={OrderList}></Route>
        <Route exact path="/orders/create" component={OrderForm} action={"create"}></Route>
        <Route exact path="/orders/:id" component={OrderItem} isItem={false}></Route>
        <Route exact path="/orders/:id/update" component={OrderForm} action={"update"}></Route>


      </BrowserRouter>
    )
  }
}

export default App;