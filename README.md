#Python 3 Web Framework inspired from DietCake

PyCake は [WebOb](http://webob.org/) をベースにした Python 3 用(>= Python 3.3)の
Web フレームワークです。

PyCake は php の Web フレームワーク [DietCake](http://dietcake.github.com/)
からコンセプトと設計の一部を受け継いでいます。

##特徴

###スケルトンフレームワーク

リクエスト、レスポンス、基本的な例外クラスは、 WebOb をそのまま利用しています。

PyCake はディスパッチャのみを実装し、モデルやビューのサポートを組み込みません。
(あとで追加するかもしれませんが、完全に分離した形にするか、 mix-in で対応する
でしょう)


###シンプルな実装

レガシーな Python 2 をサポートせず、オブジェクトモデルがシンプルな Python 3
を使って必要最小限のシンプルなメタプログラミングを用いることで、
フレームワークのユーザーにとってのブラックボックスを大きくしないようにしています。
