$(function() {
    /**
     * Ваш сайт, для примеров работы с запросами
     */
    var URL = 'http://example.com';

    /**
     * Некоторые переменные, доступные в глобальной видимости Омнидеска:
     * CurrentCaseId
     * CurrentUserId
     * CurrentStaffId
     * CurrentClientId
     * 
     * Данные в этих переменных уже можно использовать чтобы получить более развернутый результат по API Омнидеска
     * https://omnidesk.ru/api/introduction/intro
     */

    var CASE_ID = CurrentCaseId;
    var CASE_URL = document.location.href;

    /**
     * Некоторые селекторы для примеров
     */
    var HORIZONTAL_MENU_SELECTOR = '.header-container';
    var HORIZONTAL_MENU_BUTTONS_SELECTOR = '.global-actions > .global-actions-list:last-child';
    var HORIZONTAL_MENU_ELEMENTS_SELECTOR = '.primary-nav';

    var INTEGRATION_PANEL_SELECTOR = '#integrations_info_panel';
    var INFORMATION_PANEL_SELECTOR = '#info_user_info_panel';

    /** HELPERS */
    
    /**
     * Проверяем на undefined
     */
    var checkNotUndefined = function(data) {
        return (typeof data === 'undefined') ? false : true;
    }

    
    /**
     * Вставка в конец или в начало элемента
     */
    var addCode = function(selector, htmlCode, after) {
        var element = $(selector);

        if(checkNotUndefined(after) === true && after === true) {
            element.append(htmlCode);
        } else {
            element.prepend(htmlCode);
        }
    };

    /** EXAMPLES */

    /**
     * Добавляем кастомную информацию в блок о пользователе
     * 
     * Сначала заголовок
     */

    addCode(
        INFORMATION_PANEL_SELECTOR,
        `<div class="info_header clearfix">
            <p>Данные Example</p>
        </div>`,
        true
    );

    /**
     * Потом информация
     * 
     * Допустим что мы запросили информацию извне 
     * $.get(URL + '/api/users/' + CurrentUserId, data, callback);
     * 
     * и получили такой объект в callback:
     */
    var UserInfromation = {
        id: 12345,
        name: 'Василий Петров',
        tariff_name: 'Максимальный',
        support_type: 'Постоянная',
    };

    /**
     * Отображаем эту информацию
     * Результат в коде Омнидеска: https://www.dropbox.com/s/5b98ud1hwi97wu5/01_custom_block.png?dl=0
     */
    addCode(
        INFORMATION_PANEL_SELECTOR,
        `<div class="info_fields">
            <h6>Логин</h6>
            <p style="word-wrap: break-word;">${UserInfromation.name}</p>
            <h6>Ссылка на профиль</h6>
            <p style="word-wrap: break-word;"><a href="${URL}/id/${UserInfromation.id}">${UserInfromation.name}</a></p>
            <h6>Тариф</h6>
            <p style="word-wrap: break-word;">${UserInfromation.tariff_name}</p>
            <h6>Тип поддержки</h6>
            <p style="word-wrap: break-word;">${UserInfromation.support_type}</p>
        </div>`,
        true
    );

    /**
     * Пример добавления пункта в меню
     * Результат в коде Омнидеска https://www.dropbox.com/s/ymscgj7q7loj09o/02_custom_menu_item.png?dl=0
     */
    addCode(
        HORIZONTAL_MENU_ELEMENTS_SELECTOR,
        `<li class="nav-item nav-item-companies inlb">
            <a class="nav-item-url " href="#example">Example</a>
        </li>`,
        true
    );

    /**
     * Пример добавления кнопки в блоках справа
     * Результат в коде Омнидеска https://www.dropbox.com/s/i0orxacnfrjwtwo/03_custom_button_in_header.png?dl=0
     */
    addCode(
        HORIZONTAL_MENU_BUTTONS_SELECTOR,
        `<li class="global-action-item inlb force-login" title="Example">
            <a class="nav-item-url" href="#example">
                <i class="icon fi-star"></i>
            </a>
        </li>`,
        false
    );
    
    /**
     * Добавляем в горизонтальное меню цвета своей компании
     * Результат в коде Омнидеска https://www.dropbox.com/s/3vtzym61el1659z/04_custom_styles.png?dl=0
     * Результат на странице https://www.dropbox.com/s/hfo696yiffw455a/04_2_custom_styles.png?dl=0
     */
    $(document).find(HORIZONTAL_MENU_SELECTOR).css({
        'border-bottom': 'solid 2px red',
    });

    /**
     * Подключаем свой CSS в код Омнидеска. В CSS дополнительные иконки
     * Результат на странице https://www.dropbox.com/s/jde5uaykf84hsak/05_custom_css.png?dl=0
     */
    $(document)
        .find('body')
        .append('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/foundicons/3.0.0/foundation-icons.css">');

    /**
     * Получаем курсы валют и добавляем в блок интеграции. Почему бы и нет?
     * Результат в коде Омнидеска https://www.dropbox.com/s/d575h7lhhnteyw4/06_custom_data.png?dl=0
     * Результат на странице https://www.dropbox.com/s/w3dy1cekim7w3k2/06_2_custom_data.png?dl=0
     */
    $.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange', {
        'coursid' : 5,
    }, function(data) {
        //Создаем HTML для вставки
        var html = '';

        html = '<div class="right_info_panels">';
            html += '<ul>';
                if(checkNotUndefined(data.length) === true && data.length > 0) {
                    for(var index in data) {
                        var currency = data[index];

                        if(checkNotUndefined(currency.ccy) === true) {
                            html += '<li>' + currency.ccy + ' : ' + currency.buy + '</li>';
                        }
                    }
                }
            html += '</ul>';
        html += '</div>';

        //Вставка в блок
        addCode(INTEGRATION_PANEL_SELECTOR, html, false);
    }, 'json');

    /**
     * Добавляем форму и отправляем ее данные на условный сайт 
     */
    var form = '';

    form = '<form action="' + URL + '" method="POST" id="example-form">';
        form += '<input type="text" value="" name="example-name" placeholder="Example Data">';
        form += '<button>Отправить</button>';
    form += '</form>';

    addCode(INTEGRATION_PANEL_SELECTOR, form, true);

    $(document).on('submit', '#example-form', function(event) {
        event.preventDefault();
        var formEl = $(this);

        // $.post(formEl.attr('action'), {
        //     //Данные формы
        //     exampleData: formEl.find('[name="example-name"]').val(),
        //     //ID обращения
        //     case_id: CASE_ID,
        //     //Ссылка на обращение в омнидеске
        //     case_url: CASE_URL,
        // }, function(response) {
        //     formEl.append('<span style="color: green>Success!</span>');
        // });
    })

    /**
     * Добавляем падающий снег, если ваши сотрудники будут работать в Новый Год :)
     * Результат в коде Омнидеска https://www.dropbox.com/s/ilkkfmf81s63zjw/07_snow.png?dl=0
     * Результат на странице: https://www.dropbox.com/s/yp36vle7yu7vm38/07_2_snow.png?dl=0
     */
    $.get('https://cdnjs.cloudflare.com/ajax/libs/JQuery-Snowfall/1.7.4/snowfall.jquery.min.js', {

    }, function(jsLibCode) {
        $("body").append($("<script />", {
            html: jsLibCode + ' $(document).snowfall({flakeColor : "yellow", shadow: true});',
        }));
    });

    /**
     * Таким образом можно менять и добавлять любые кнопки, формы и код на странице обращения.
     */
});