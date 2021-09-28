import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'react-router-dom'
import axiosInstance from '../../database/axios'


const AvailableWalletList = (props) => {
    const username = props.username

    const GetWallets = async () => {
        const results = await axiosInstance.get(`/accounts/${username}/`)
        return await results.wallets
    }

    const handleRemove = (e) => {
        const listItem = e.target.parent.parent
        console.log(listItem);
        const wallet = listItem.id
        const name = wallet.strip(' ')[0]
        if (window.confirm(`Вы действительно хотите убрать кошелёк ${name} из доступных?`)) {
            listItem.remove()
            axiosInstance.delete(`/wallets/${name}/remove/`)
                .then((response) => response.data)
                .then((data) => {
                    console.log(data);
                })
        }
    }

    GetWallets()
        .then((wallets) => (
            <ul className="wallet-list">
                {
                    wallets.length > 0
                        ?
                        wallets.map((wallet) => (
                            <li key={wallet} className="wallet-item" id={wallet}>
                                <div className="wallet-icon">
                                    <FontAwesomeIcon icon={['fas', 'wallet']} />
                                </div>
                                <div className="wallet-info">
                                    {wallet}
                                </div>
                                <div className="wallet-action-group">
                                    <div className="wallet-action-item" onClick={handleRemove}>
                                        <FontAwesomeIcon icon={['fas', 'trash-alt']} />
                                    </div>
                                </div>
                            </li>
                        ))
                        :
                        <h2>У вас ещё нет кошельков. Добавьте парочку, это удобно.</h2>
                }

                <div className="flex-container align-center" style={{ paddingBottom: "30px" }}>
                    <Link to="/profile/addwallet">
                        <button type="button" className="create-order-btn">
                            Добавить кошелёк
                        </button>
                    </Link>
                </div>
            </ul>
        ))
        .catch((errors) => {
            console.log(errors.data);
        })
    return <h2>Error while loading list occured</h2>
}

export default AvailableWalletList;