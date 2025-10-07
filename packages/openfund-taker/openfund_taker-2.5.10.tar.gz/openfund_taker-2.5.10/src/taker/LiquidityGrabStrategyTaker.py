# -*- coding: utf-8 -*-
from typing import override
from cachetools import TTLCache
from core.smc.TF import TF
from core.utils.OPTools import OPTools
from taker.StrategyTaker import StrategyTaker


class LiquidityGrabStrategyTaker(StrategyTaker):
    """
    流动性抓取形态策略Taker端
    负责基于流动性目标的止盈止损管理
    """

    def __init__(
        self, g_config, platform_config, common_config, logger=None, exchangeKey="okx"
    ) -> None:
        super().__init__(
            g_config=g_config,
            platform_config=platform_config,
            common_config=common_config,
            logger=logger,
            exchangeKey=exchangeKey,
        )

        # 流动性抓取特有的状态追踪
        self.has_init_SL_TPs = {}  # 是否已初始化止盈止损
        self.liquidity_targets = {}  # 流动性目标追踪
        self.order_block_levels = {}  # 订单块水平追踪
        self.entering_liquidity_tps = {}  # 进入流动性止盈监控

        cache_ttl = common_config.get("cache_ttl", 60)
        self.htf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl * 60))
        self.atf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl * 60))

    @override
    def reset_SL_TP(self, symbol=None, attachType="BOTH"):
        """重置止盈止损状态"""
        super().reset_SL_TP(symbol, attachType)
        if not symbol:
            self.has_init_SL_TPs.clear()
            self.liquidity_targets.clear()
            self.order_block_levels.clear()
            self.entering_liquidity_tps.clear()
        elif attachType == self.BOTH_KEY and symbol in self.has_init_SL_TPs:
            self.has_init_SL_TPs.pop(symbol, None)
            self.liquidity_targets.pop(symbol, None)
            self.order_block_levels.pop(symbol, None)
            self.entering_liquidity_tps.pop(symbol, None)

    def init_liquidity_grab_SL_TP(
        self, symbol: str, position, tfs: dict, strategy: dict
    ) -> bool:
        """
        基于流动性抓取策略的止盈止损初始化
        止损：基于ATF订单块边界
        止盈：基于等高/等低流动性位置
        """
        open_body_break = bool(strategy.get("open_body_break", True))
        stop_loss_buffer_ticks = int(strategy.get("stop_loss_buffer_ticks", 2))
        min_profit_ratio = OPTools.ensure_decimal(strategy.get("min_profit_ratio", 1.5))

        precision = self.get_precision_length(symbol)
        pos_side = position[self.SIDE_KEY]
        side = self.SELL_SIDE if pos_side == self.SHORT_KEY else self.BUY_SIDE

        htf = tfs[self.HTF_KEY]
        atf = tfs[self.ATF_KEY]
        etf = tfs[self.ETF_KEY]

        # 1. 获取ATF数据分析支撑阻力位和订单块
        atf_df = self.get_historical_klines_df(symbol=symbol, tf=atf)
        atf_struct = self.build_struct(
            symbol=symbol, data=atf_df, is_struct_body_break=open_body_break
        )
        atf_OBs_df = self.find_OBs(
            symbol=symbol, struct=atf_struct, is_struct_body_break=open_body_break
        )

        atf_support_resistance = self.get_support_resistance_from_OBs(
            symbol=symbol, obs_df=atf_OBs_df, struct_df=atf_struct
        )

        if atf_support_resistance is None:
            self.logger.info(
                f"{symbol} : ATF {atf} 未找到支撑阻力位，使用默认百分比止盈止损"
            )
            return self._init_default_SL_TP(symbol, position, strategy)

        # 2. 识别等高等低流动性目标
        liquidity_target = self._identify_liquidity_target(
            symbol, atf_df, atf_struct, pos_side, strategy
        )

        if not liquidity_target:
            self.logger.info(f"{symbol} : ATF {atf} 未找到流动性目标，使用支撑阻力位")
            return self._init_support_resistance_SL_TP(
                symbol, position, atf_support_resistance, stop_loss_buffer_ticks
            )

        # 3. 计算基于流动性的止盈止损
        tick_size = self.get_tick_size(symbol)
        price_offset = stop_loss_buffer_ticks * tick_size

        atf_support_OB = atf_support_resistance.get(self.SUPPORT_OB_KEY)
        atf_resistance_OB = atf_support_resistance.get(self.RESISTANCE_OB_KEY)

        if pos_side == self.LONG_KEY:
            # 多头：止损=支撑位下方订单块底部-缓冲，止盈=等高流动性
            if atf_support_OB:
                sl_price = self.toDecimal(
                    atf_support_OB[self.OB_LOW_COL]
                ) - self.toDecimal(price_offset)
                self.order_block_levels[symbol] = atf_support_OB[self.OB_LOW_COL]
            else:
                sl_price = self.toDecimal(
                    atf_support_resistance[self.SUPPORT_PRICE_KEY]
                ) - self.toDecimal(price_offset)

            tp_price = self.toDecimal(liquidity_target["price"]) + self.toDecimal(
                price_offset
            )

            # 设置进入流动性监控的触发价格
            if atf_resistance_OB:
                entering_trigger_price = atf_resistance_OB[self.OB_HIGH_COL]
            else:
                entering_trigger_price = atf_support_resistance[
                    self.RESISTANCE_PRICE_KEY
                ]

        else:
            # 空头：止损=阻力位上方订单块顶部+缓冲，止盈=等低流动性
            if atf_resistance_OB:
                sl_price = self.toDecimal(
                    atf_resistance_OB[self.OB_HIGH_COL]
                ) + self.toDecimal(price_offset)
                self.order_block_levels[symbol] = atf_resistance_OB[self.OB_HIGH_COL]
            else:
                sl_price = self.toDecimal(
                    atf_support_resistance[self.RESISTANCE_PRICE_KEY]
                ) + self.toDecimal(price_offset)

            tp_price = self.toDecimal(liquidity_target["price"]) - self.toDecimal(
                price_offset
            )

            # 设置进入流动性监控的触发价格
            if atf_support_OB:
                entering_trigger_price = atf_support_OB[self.OB_LOW_COL]
            else:
                entering_trigger_price = atf_support_resistance[self.SUPPORT_PRICE_KEY]

        # 4. 验证盈亏比
        entry_price = self.toDecimal(position[self.ENTRY_PRICE_KEY])
        profit_distance = abs(tp_price - entry_price)
        loss_distance = abs(entry_price - sl_price)

        if loss_distance > 0:
            actual_ratio = profit_distance / loss_distance
            if actual_ratio < min_profit_ratio:
                self.logger.info(
                    f"{symbol} : 盈亏比{actual_ratio:.2f} < {min_profit_ratio}，调整止盈价格"
                )
                # 调整止盈价格以满足最小盈亏比
                if pos_side == self.LONG_KEY:
                    tp_price = OPTools.safe_decimal_add(
                        entry_price,
                        OPTools.safe_decimal_multiply(loss_distance, min_profit_ratio),
                    )
                else:
                    tp_price = OPTools.safe_decimal_subtract(
                        entry_price,
                        OPTools.safe_decimal_multiply(loss_distance, min_profit_ratio),
                    )

        self.logger.info(
            f"{symbol} : 流动性抓取止盈止损 - 入场={entry_price:.{precision}f}, 止损={sl_price:.{precision}f}, 止盈={tp_price:.{precision}f}"
        )

        # 5. 设置止盈止损
        self.cancel_all_algo_orders(symbol=symbol, attachType=self.TP_KEY)
        has_tp = self.set_take_profit(
            symbol=symbol, position=position, tp_price=tp_price
        )

        self.cancel_all_algo_orders(symbol=symbol, attachType=self.SL_KEY)
        try:
            has_sl = self.set_stop_loss(
                symbol=symbol, position=position, sl_price=sl_price
            )
        except ValueError as e:
            self.logger.warning(f"{symbol} : 设置止损失败，使用默认方式: {e}")
            return self._init_default_SL_TP(symbol, position, strategy)

        # 6. 保存流动性目标和监控信息
        self.liquidity_targets[symbol] = liquidity_target
        self.entering_liquidity_tps[symbol] = entering_trigger_price

        return has_tp and has_sl

    def _identify_liquidity_target(
        self, symbol, atf_df, atf_struct, pos_side, strategy
    ):
        """识别等高等低流动性目标"""
        atf_latest_struct = self.get_latest_struct(symbol=symbol, data=atf_struct)
        if not atf_latest_struct:
            return None

        trend = atf_latest_struct[self.STRUCT_DIRECTION_COL]

        # 根据持仓方向确定要寻找的流动性类型
        if pos_side == self.LONG_KEY:
            # 多头寻找等高流动性作为止盈目标
            target_trend = self.BULLISH_TREND
            end_idx = atf_latest_struct[self.STRUCT_HIGH_INDEX_COL]
        else:
            # 空头寻找等低流动性作为止盈目标
            target_trend = self.BEARISH_TREND
            end_idx = atf_latest_struct[self.STRUCT_LOW_INDEX_COL]

        # 使用SMCLiquidity查找等高等低
        atr_offset = strategy.get("liquidity_atr_offset", 0.0003)
        last_EQ = self.find_EQH_EQL(
            symbol=symbol,
            data=atf_df,
            trend=target_trend,
            end_idx=end_idx,
            atr_offset=atr_offset,
        )

        if not last_EQ or not last_EQ.get(self.HAS_EQ_KEY):
            return None

        if pos_side == self.LONG_KEY and self.EQUAL_HIGH_COL in last_EQ:
            return {
                "price": last_EQ[self.EQUAL_HIGH_COL],
                "type": "equal_high",
                "trend": target_trend,
            }
        elif pos_side == self.SHORT_KEY and self.EQUAL_LOW_COL in last_EQ:
            return {
                "price": last_EQ[self.EQUAL_LOW_COL],
                "type": "equal_low",
                "trend": target_trend,
            }

        return None

    def _init_default_SL_TP(self, symbol, position, strategy):
        """使用默认百分比的止盈止损"""
        stop_loss_pct = OPTools.ensure_decimal(strategy.get("stop_loss_pct", 2))
        take_profile_pct = OPTools.ensure_decimal(strategy.get("take_profile_pct", 2))

        sl_price = self.calculate_sl_price_by_pct(
            symbol=symbol, position=position, sl_pct=stop_loss_pct
        )
        tp_price = self.calculate_tp_price_by_pct(
            symbol=symbol, position=position, tp_pct=take_profile_pct
        )

        self.cancel_all_algo_orders(symbol=symbol, attachType=self.TP_KEY)
        has_tp = self.set_take_profit(
            symbol=symbol, position=position, tp_price=tp_price
        )

        self.cancel_all_algo_orders(symbol=symbol, attachType=self.SL_KEY)
        has_sl = self.set_stop_loss(symbol=symbol, position=position, sl_price=sl_price)

        return has_tp and has_sl

    def _init_support_resistance_SL_TP(
        self, symbol, position, support_resistance, buffer_ticks
    ):
        """基于支撑阻力位的止盈止损"""
        tick_size = self.get_tick_size(symbol)
        price_offset = buffer_ticks * tick_size
        pos_side = position[self.SIDE_KEY]

        if pos_side == self.LONG_KEY:
            sl_price = self.toDecimal(
                support_resistance[self.SUPPORT_PRICE_KEY]
            ) - self.toDecimal(price_offset)
            tp_price = self.toDecimal(
                support_resistance[self.RESISTANCE_PRICE_KEY]
            ) + self.toDecimal(price_offset)
        else:
            sl_price = self.toDecimal(
                support_resistance[self.RESISTANCE_PRICE_KEY]
            ) + self.toDecimal(price_offset)
            tp_price = self.toDecimal(
                support_resistance[self.SUPPORT_PRICE_KEY]
            ) - self.toDecimal(price_offset)

        self.cancel_all_algo_orders(symbol=symbol, attachType=self.TP_KEY)
        has_tp = self.set_take_profit(
            symbol=symbol, position=position, tp_price=tp_price
        )

        self.cancel_all_algo_orders(symbol=symbol, attachType=self.SL_KEY)
        has_sl = self.set_stop_loss(symbol=symbol, position=position, sl_price=sl_price)

        return has_tp and has_sl

    def check_liquidity_grab_TP(
        self, symbol: str, position, tfs, strategy: dict
    ) -> bool:
        """
        流动性抓取特有的止盈监控
        监控价格是否触及流动性目标区域，并确认LTF结构反转
        """
        if (
            symbol not in self.entering_liquidity_tps
            or symbol not in self.liquidity_targets
        ):
            return False

        entering_trigger_price = self.entering_liquidity_tps[symbol]
        liquidity_target = self.liquidity_targets[symbol]
        market_price = position[self.MARK_PRICE_KEY]
        pos_side = position[self.SIDE_KEY]

        # 检查是否进入流动性监控区域
        if pos_side == self.LONG_KEY:
            in_monitoring_zone = market_price >= entering_trigger_price
        else:
            in_monitoring_zone = market_price <= entering_trigger_price

        if not in_monitoring_zone:
            return False

        precision = self.get_precision_length(symbol)
        self.logger.info(
            f"{symbol} : 进入流动性监控区域，当前价格{market_price:.{precision}f}，触发价格{entering_trigger_price:.{precision}f}"
        )

        # 检查是否接近流动性目标
        target_price = liquidity_target["price"]
        target_tolerance = 0.3  # 0.3%容差
        price_diff_pct = abs(market_price - target_price) / target_price * 100

        if price_diff_pct > target_tolerance:
            self.logger.debug(
                f"{symbol} : 距离流动性目标{target_price:.{precision}f}还有{price_diff_pct:.2f}%"
            )
            return False

        # 检查LTF结构反转确认
        open_body_break = strategy.get("open_body_break", True)
        etf = tfs[self.ETF_KEY]

        etf_df = self.get_historical_klines_df(symbol=symbol, tf=etf)
        etf_struct = self.build_struct(
            symbol=symbol, data=etf_df, is_struct_body_break=open_body_break
        )
        etf_latest_struct = self.get_latest_struct(
            symbol=symbol, data=etf_struct, is_struct_body_break=open_body_break
        )

        if not etf_latest_struct:
            self.logger.debug(f"{symbol} : LTF {etf} 未形成结构")
            return False

        etf_trend = etf_latest_struct[self.STRUCT_DIRECTION_COL]
        expected_trend = (
            self.BULLISH_TREND if pos_side == self.LONG_KEY else self.BEARISH_TREND
        )

        if etf_trend != expected_trend:
            self.logger.debug(
                f"{symbol} : LTF {etf} 结构{etf_trend}与预期{expected_trend}不符"
            )
            return False

        # 检查结构类型，CHOCH或BOS更可靠
        etf_struct_type = etf_latest_struct[self.STRUCT_COL]
        if etf_struct_type and ("CHOCH" in etf_struct_type or "BOS" in etf_struct_type):
            self.logger.info(
                f"{symbol} : LTF {etf} 结构反转确认 {etf_struct_type}，触发流动性止盈"
            )
            return True

        return False

    def trailing_SL_by_order_blocks(self, symbol: str, position, tfs, strategy: dict):
        """
        基于订单块的移动止损
        使用有效的订单块作为新的止损位
        """
        if symbol not in self.order_block_levels:
            return

        open_body_break = strategy.get("open_body_break", True)
        trailing_atr_multiplier = strategy.get("trailing_order_block_atr", 0.6)
        precision = self.get_precision_length(symbol)

        etf = tfs[self.ETF_KEY]
        pos_side = position[self.SIDE_KEY]
        market_price = position[self.MARK_PRICE_KEY]

        # 获取LTF数据寻找新的订单块
        etf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=etf)
        etf_struct = self.build_struct(
            symbol=symbol, data=etf_df, is_struct_body_break=open_body_break
        )

        # 寻找有效的订单块
        side = (
            self.SELL_SIDE if pos_side == self.LONG_KEY else self.BUY_SIDE
        )  # 寻找反向订单块
        etf_OBs_df = self.find_OBs(
            symbol=symbol,
            struct=etf_struct,
            side=side,
            is_valid=True,
            is_struct_body_break=open_body_break,
            atr_multiplier=trailing_atr_multiplier,
        )

        if len(etf_OBs_df) == 0:
            self.logger.debug(f"{symbol} : 未找到有效的订单块用于移动止损")
            return

        # 过滤出符合条件的订单块
        if pos_side == self.LONG_KEY:
            # 多头：寻找当前价格下方的订单块作为新止损
            mask = etf_OBs_df[self.OB_HIGH_COL] < market_price
        else:
            # 空头：寻找当前价格上方的订单块作为新止损
            mask = etf_OBs_df[self.OB_LOW_COL] > market_price

        filtered_OBs = etf_OBs_df[mask]
        if len(filtered_OBs) == 0:
            return

        # 选择最新的订单块
        latest_OB = filtered_OBs.iloc[-1]

        # 验证订单块质量（大实体+小影线）
        if not self._validate_order_block_quality(latest_OB, strategy):
            return

        # 计算新的止损价格
        tick_size = self.get_tick_size(symbol)
        buffer_ticks = strategy.get("stop_loss_buffer_ticks", 2)
        price_offset = buffer_ticks * tick_size

        if pos_side == self.LONG_KEY:
            new_sl_price = self.toDecimal(latest_OB[self.OB_LOW_COL]) - self.toDecimal(
                price_offset
            )
        else:
            new_sl_price = self.toDecimal(latest_OB[self.OB_HIGH_COL]) + self.toDecimal(
                price_offset
            )

        # 验证新止损是否更优
        current_sl_price = self.get_stop_loss_price(symbol)
        should_update = False

        if current_sl_price is None:
            should_update = True
        elif pos_side == self.LONG_KEY and new_sl_price > current_sl_price:
            should_update = True
        elif pos_side == self.SHORT_KEY and new_sl_price < current_sl_price:
            should_update = True

        if should_update:
            self.logger.info(
                f"{symbol} : 基于订单块移动止损 {current_sl_price} -> {new_sl_price:.{precision}f}"
            )
            self.cancel_all_algo_orders(symbol=symbol, attachType=self.SL_KEY)
            self.set_stop_loss(symbol=symbol, position=position, sl_price=new_sl_price)
            self.order_block_levels[symbol] = (
                latest_OB[self.OB_LOW_COL]
                if pos_side == self.LONG_KEY
                else latest_OB[self.OB_HIGH_COL]
            )
        else:
            self.logger.debug(
                f"{symbol} : 新订单块止损{new_sl_price:.{precision}f}不优于当前止损{current_sl_price}"
            )

    def _validate_order_block_quality(self, order_block, strategy):
        """验证订单块质量（大实体+小影线标准）"""
        min_body_ratio = strategy.get("order_block_filter", {}).get(
            "min_body_ratio", 0.7
        )
        max_wick_ratio = strategy.get("order_block_filter", {}).get(
            "max_wick_ratio", 0.3
        )

        # 这里简化处理，实际应该根据订单块对应的K线数据来计算
        # 由于订单块数据中没有直接的实体和影线信息，暂时返回True
        # 在实际应用中可以通过订单块的timestamp找到对应的K线进行详细分析
        return True

    @override
    def process_pair(self, symbol: str, position, pair_config: dict) -> None:
        """处理单个交易对的流动性抓取策略"""
        precision = self.get_precision_length(symbol)

        liquidity_strategy = pair_config.get("liquidity_grab_strategy", {})
        stop_loss_pct = OPTools.ensure_decimal(pair_config.get("all_stop_loss_pct", 2))
        all_TP_SL_ratio = OPTools.ensure_decimal(
            pair_config.get("all_TP_SL_ratio", 1.5)
        )

        # 时间框架配置
        tfs = {
            self.HTF_KEY: str(liquidity_strategy.get("htf", "4h")),
            self.ATF_KEY: str(liquidity_strategy.get("atf", "15m")),
            self.ETF_KEY: str(liquidity_strategy.get("etf", "1m")),
        }

        htf, atf, etf = tfs[self.HTF_KEY], tfs[self.ATF_KEY], tfs[self.ETF_KEY]

        # 更新策略参数
        liquidity_strategy["stop_loss_pct"] = stop_loss_pct
        liquidity_strategy["take_profile_pct"] = OPTools.safe_decimal_multiply(
            stop_loss_pct, all_TP_SL_ratio
        )

        open_body_break = bool(liquidity_strategy.get("open_body_break", True))
        self.logger.info(
            f"{symbol} : 流动性抓取策略 {htf}|{atf}|{etf} open_body_break={open_body_break}"
        )

        # 1. 初始化流动性抓取止盈止损
        if symbol not in self.has_init_SL_TPs:
            has_pass = self.init_liquidity_grab_SL_TP(
                symbol, position, tfs, liquidity_strategy
            )

            if has_pass:
                self.has_init_SL_TPs[symbol] = True
                self.logger.info(f"{symbol} : 流动性抓取止盈止损初始化成功")
            else:
                self.logger.info(f"{symbol} : 流动性抓取止盈止损初始化失败")

        # 2. 基于订单块的移动止损
        enable_order_block_trailing = liquidity_strategy.get(
            "enable_order_block_trailing", True
        )
        if enable_order_block_trailing:
            self.logger.debug(f"{symbol} : 开启订单块移动止损...")
            self.trailing_SL_by_order_blocks(symbol, position, tfs, liquidity_strategy)

        # 3. 流动性目标止盈监控
        enable_liquidity_target_tp = liquidity_strategy.get(
            "enable_liquidity_target_tp", True
        )
        tp_structure_confirmation = liquidity_strategy.get(
            "tp_structure_confirmation", True
        )

        if enable_liquidity_target_tp and tp_structure_confirmation:
            if not self.check_liquidity_grab_TP(
                symbol, position, tfs, liquidity_strategy
            ):
                self.logger.debug(f"{symbol} : 未触发流动性止盈监控，等待...")
            else:
                order = self.close_position(symbol, position)
                if order:
                    self.logger.info(
                        f"{symbol} : 流动性目标达成，市价{position[self.MARK_PRICE_KEY]:.{precision}f}平仓"
                    )
