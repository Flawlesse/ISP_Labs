import React from 'react';
import './App.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { fab } from '@fortawesome/free-brands-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { BrowserRouter, Route, Redirect, Switch } from 'react-router-dom'
import { axiosInstance, axiosMultipartInstance } from '../database/axios'
import LoginForm from './auth/LoginForm'
import Logout from './auth/Logout'
import AccountForm from './account/AccountForm'
import OrderList from './order/OrderList'
import OrderItem from './order/OrderItem'
import OrderForm from './order/OrderForm'
import AccountDetail from "./account/AccountDetail"
import Navbar from './Navbar'
import Profile from './account/Profile'
import AddWalletForm from './account/AddWalletForm'

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

  appLogin = () => {
    this.setState({ loggedIn: true })
  }
  appLogout = () => {
    window.localStorage.removeItem('access_token')
    window.dispatchEvent(new StorageEvent('storage', {
      storageArea: window.localStorage,
      key: "access_token",
      newValue: null,
    }))
    this.setState({
      loggedIn: false,
    })
  }

  getCurrentUsername = async () => {
    try {
      const results = await axiosMultipartInstance.get('profile/')
      return results.data.username
    }
    catch (error) {
      return null
    }
  }

  render() {
    return (
      <BrowserRouter>
        <Navbar />
        <Switch>
          <Route exact path="/profile" render={
            (props) => <Profile {...props} />
          } />
          <Route exact path="/profile/addwallet" render={
            (props) =>
              <AddWalletForm
                {...props}
              />
          } />
          <Route exact path="/accounts/login" render={
            (props) =>
              <LoginForm
                {...props}
                appLogin={this.appLogin}
              />}
          />
          <Route exact path="/accounts/logout" render={
            (props) =>
              <Logout
                {...props}
                appLogout={this.appLogout}
              />}
          />
          <Route exact path="/accounts/register" render={
            (props) =>
              <AccountForm
                {...props}
                appLogin={this.appLogin}
                appLogout={this.appLogout}
                action={"register"}
              />}
          />
          <Route exact path="/accounts/:username" component={AccountDetail} />
          <Route exact path="/accounts/:username/update" render={
            (props) =>
              <AccountForm
                {...props}
                appLogin={this.appLogin}
                appLogout={this.appLogout}
                action={"update"}
              />}
          />


          <Route exact path="/"><Redirect to="/orders" /></Route>
          <Route exact path="/orders" render={
            (props) => <OrderList {...props} isLoggedIn={this.state.loggedIn} />
          }>
          </Route>
          <Route exact path="/orders/create" render={
            (props) => <OrderForm {...props} action={"create"} isLoggedIn={this.state.loggedIn} />
          } />
          <Route exact path="/orders/:id" component={(props) => <OrderItem {...props} isItem={false} />}></Route>
          <Route exact path="/orders/:id/update" component={
            (props) => <OrderForm {...props} action={"update"} isLoggedIn={this.state.loggedIn} />
          } />
        </Switch>
      </BrowserRouter>
    )
  }
}

export default App;